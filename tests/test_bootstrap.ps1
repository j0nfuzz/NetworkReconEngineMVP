$ErrorActionPreference = "Stop"

# Extract the target function definitions from the bootstrap script using the AST
# so we never execute the script body or interactive parameter blocks.
$script:BatDir = Join-Path $PSScriptRoot '..' -Resolve
$script:BatPath = Join-Path $script:BatDir 'interactive_bootstrap.ps1'
$script:BatSource = Get-Content -LiteralPath $script:BatPath -Raw
$script:Ast = [System.Management.Automation.Language.Parser]::ParseInput($script:BatSource, [ref]$null, [ref]$null)
$script:TargetNames = @('Find-PythonInterpreter', 'Test-VenvHealthy', 'Remove-Venv', 'Ensure-Venv')
foreach ($func in $script:Ast.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)) {
    if ($func.Name -in $script:TargetNames) {
        # Define in global scope so Pester test blocks can invoke them.
        . ([scriptblock]::Create('function global:' + $func.Name + ' ' + $func.Body.Extent.Text))
    }
}

BeforeAll {
    $script:OriginalPWD = Get-Location
    $script:OriginalPath = $env:PATH
    $script:TestRoot = Join-Path $env:TEMP ('BootstrapTests_' + [Guid]::NewGuid().ToString().Substring(0, 8))
    New-Item -ItemType Directory -Path $script:TestRoot -Force | Out-Null
    Set-Location $script:TestRoot
}

AfterAll {
    Set-Location $script:OriginalPWD
    $env:PATH = $script:OriginalPath
    if (Test-Path $script:TestRoot) {
        Remove-Item -LiteralPath $script:TestRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Describe "Find-PythonInterpreter" {
    It "returns an existing python executable via py or PATH python" {
        $interpreter = Find-PythonInterpreter
        $interpreter | Should -Not -BeNullOrEmpty
        Test-Path $interpreter | Should -Be $true
    }

    It "prefers py launcher over PATH python" -Skip:(-not (Get-Command 'py' -ErrorAction SilentlyContinue)) {
        $interpreter = Find-PythonInterpreter
        # If both py and PATH python exist, the returned path should match the
        # py-launched interpreter, not an arbitrary PATH python.
        $pyPath = (& py -c "import sys; print(sys.executable)" 2>$null)
        if ($pyPath -is [array]) { $pyPath = $pyPath[0] }
        $pyPath = ([string]$pyPath).Trim()
        $interpreter | Should -Be $pyPath
    }

    It "falls back to PATH python when py launcher is unavailable" {
        # Simulate an environment where `py` fails by shadowing it with a script
        # that reports an unsupported version, forcing use of PATH `python`.
        $shadowDir = Join-Path $script:TestRoot 'shadow_py'
        New-Item -ItemType Directory -Path $shadowDir -Force | Out-Null
        try {
            $env:PATH = "$shadowDir;$($env:PATH)"
            Set-Content -LiteralPath (Join-Path $shadowDir 'py.ps1') -Value 'Write-Output "C:\fake\python.exe"; Write-Output "3"; Write-Output "8"' -Encoding UTF8
            $interpreter = Find-PythonInterpreter
            $interpreter | Should -Not -BeNullOrEmpty
            Test-Path $interpreter | Should -Be $true
        }
        finally {
            $env:PATH = $script:OriginalPath
        }
    }

    It "returns null when no usable Python 3.12+ exists" {
        # Shadow both candidates with scripts that report an unsupported version.
        $shadowDir = Join-Path $script:TestRoot 'no_python'
        New-Item -ItemType Directory -Path $shadowDir -Force | Out-Null
        try {
            $env:PATH = "$shadowDir;$($env:PATH)"
            Set-Content -LiteralPath (Join-Path $shadowDir 'py.ps1') -Value 'Write-Output "C:\fake\python.exe"; Write-Output "3"; Write-Output "8"' -Encoding UTF8
            Set-Content -LiteralPath (Join-Path $shadowDir 'python.ps1') -Value 'Write-Output "C:\fake\python.exe"; Write-Output "3"; Write-Output "8"' -Encoding UTF8
            Find-PythonInterpreter | Should -BeNullOrEmpty
        }
        finally {
            $env:PATH = $script:OriginalPath
        }
    }
}

Describe "Test-VenvHealthy" {
    It "returns false for a missing venv directory" {
        Test-VenvHealthy -VenvDir (Join-Path $script:TestRoot 'does-not-exist') | Should -Be $false
    }

    It "returns true for a freshly created healthy venv" -Skip:(-not (Find-PythonInterpreter)) {
        $venv = Join-Path $script:TestRoot 'healthy_venv'
        & (Find-PythonInterpreter) -m venv $venv
        Test-VenvHealthy -VenvDir $venv | Should -Be $true
    }

    It "returns false when pyvenv.cfg exists but interpreter is missing" -Skip:(-not (Find-PythonInterpreter)) {
        $venv = Join-Path $script:TestRoot 'broken_venv'
        & (Find-PythonInterpreter) -m venv $venv
        Remove-Item -LiteralPath (Join-Path $venv 'Scripts\python.exe') -Force
        Test-VenvHealthy -VenvDir $venv | Should -Be $false
    }

    It "returns false when pyvenv.cfg references a stale interpreter path while python.exe remains" -Skip:(-not (Find-PythonInterpreter)) {
        $venv = Join-Path $script:TestRoot 'stale_venv'
        & (Find-PythonInterpreter) -m venv $venv
        # Simulate a copied/synced venv pointing to a non-existent profile path.
        $cfg = Join-Path $venv 'pyvenv.cfg'
        $content = Get-Content -LiteralPath $cfg -Raw
        $content = $content -replace '^(home\s*=\s*).*', "`$1C:\\Users\\USERNAME\\AppData\\Local\\Programs\\Python\\Python312"
        Set-Content -LiteralPath $cfg -Value $content -Encoding UTF8 -NoNewline
        # Do NOT touch python.exe: the failure must come from the stale home reference.
        Test-VenvHealthy -VenvDir $venv | Should -Be $false
    }

    It "returns false when venv python exits with non-zero code" -Skip:(-not (Find-PythonInterpreter)) {
        $venv = Join-Path $script:TestRoot 'nonzero_venv'
        & (Find-PythonInterpreter) -m venv $venv
        # Replace the venv python.exe with a tiny executable that always exits 1.
        $fakeExe = Join-Path $script:TestRoot 'fake_python.cs'
        Set-Content -LiteralPath $fakeExe -Value 'class P { static int Main() { return 1; } }' -Encoding UTF8
        $compiler = Join-Path $env:windir 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
        if (-not (Test-Path $compiler)) {
            Set-ItResult -Skipped -Because 'csc.exe is unavailable on this machine'
        }
        & $compiler /target:exe /out:"$($script:TestRoot)\fake_python.exe" $fakeExe | Out-Null
        Copy-Item -LiteralPath (Join-Path $script:TestRoot 'fake_python.exe') -Destination (Join-Path $venv 'Scripts\python.exe') -Force
        Test-VenvHealthy -VenvDir $venv | Should -Be $false
    }
}

Describe "Ensure-Venv" {
    It "creates a new venv when none exists" -Skip:(-not (Find-PythonInterpreter)) {
        $venv = Join-Path $script:TestRoot 'ensure_create_venv'
        $req = Join-Path $script:TestRoot 'requirements.txt'
        "# no deps" | Set-Content -LiteralPath $req -Encoding UTF8
        Ensure-Venv -VenvDir $venv -RequirementsFile $req
        Test-Path (Join-Path $venv 'Scripts\python.exe') | Should -Be $true
    }

    It "reuses a healthy venv without recreating" -Skip:(-not (Find-PythonInterpreter)) {
        $venv = Join-Path $script:TestRoot 'ensure_reuse_venv'
        $req = Join-Path $script:TestRoot 'requirements2.txt'
        "# no deps" | Set-Content -LiteralPath $req -Encoding UTF8
        & (Find-PythonInterpreter) -m venv $venv
        $before = Get-Item (Join-Path $venv 'Scripts\python.exe')
        Ensure-Venv -VenvDir $venv -RequirementsFile $req
        $after = Get-Item (Join-Path $venv 'Scripts\python.exe')
        $after.LastWriteTime | Should -Be $before.LastWriteTime
    }

    It "recreates a stale venv automatically" -Skip:(-not (Find-PythonInterpreter)) {
        $venv = Join-Path $script:TestRoot 'ensure_recreate_venv'
        $req = Join-Path $script:TestRoot 'requirements3.txt'
        "# no deps" | Set-Content -LiteralPath $req -Encoding UTF8
        & (Find-PythonInterpreter) -m venv $venv
        Remove-Item -LiteralPath (Join-Path $venv 'Scripts\python.exe') -Force
        Ensure-Venv -VenvDir $venv -RequirementsFile $req
        Test-Path (Join-Path $venv 'Scripts\python.exe') | Should -Be $true
    }
}
