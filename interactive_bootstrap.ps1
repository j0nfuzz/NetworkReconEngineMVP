param(
    [string]$TargetHost = "",
    [string]$Username = "",
    [string]$Password = "",
    [string]$Vendor = "auto",
    [int]$Port = 22,
    [int]$Timeout = 15,
    [string]$OutputDir = "output",
    [ValidateSet('auto', 'reject', 'warning')]
    [string]$HostKeyPolicy = "auto",
    [string]$KnownHosts = "",
    [ValidateSet('auto', 'modern', 'legacy')]
    [string]$ParamikoProfile = 'auto',
    [switch]$Verbose,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

function Convert-SecureStringToPlainText {
    param([System.Security.SecureString]$SecureString)
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)
    try {
        return [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

function Get-InputValue {
    param(
        [string]$Prompt,
        [string]$DefaultValue = "",
        [switch]$AsSecureString
    )
    $message = if ($DefaultValue) { "${Prompt} [$DefaultValue]: " } else { "${Prompt}: " }
    if ($AsSecureString) {
        $secureValue = Read-Host -Prompt $message -AsSecureString
        $value = Convert-SecureStringToPlainText -SecureString $secureValue
    }
    else {
        $value = Read-Host -Prompt $message
    }
    # Fall back to the displayed default on a blank answer.
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $DefaultValue
    }
    return $value
}

function ConvertTo-YamlStr {
    param([string]$Value)
    if ([string]::IsNullOrEmpty($Value)) { return "''" }
    return "'" + ($Value -replace "'", "''") + "'"
}

function Ensure-Venv {
    param([string]$VenvDir, [string]$RequirementsFile)
    if (-not (Test-Path $VenvDir)) {
        Write-Host "Creating virtual environment '$VenvDir' ..."
        python -m venv $VenvDir
    }
    if (-not $SkipInstall) {
        Write-Host "Installing dependencies ($RequirementsFile) into '$VenvDir' ..."
        & "$VenvDir\Scripts\python.exe" -m pip install -r $RequirementsFile
    }
    else {
        Write-Host "Skipping dependency install (-SkipInstall) for '$VenvDir'."
    }
}

Write-Host ""
Write-Host "=== Network Device Diagnostics Collector ==="

# Prompt for session / environment variables (values passed as params are used as defaults).
if (-not $TargetHost) { $TargetHost = Get-InputValue -Prompt "Device IP/hostname" }
if (-not $Username)   { $Username   = Get-InputValue -Prompt "SSH username" }
if (-not $Password)   { $Password   = Get-InputValue -Prompt "SSH password" -AsSecureString }
if (-not $PSBoundParameters.ContainsKey('Port')) {
    $portValue = Get-InputValue -Prompt "SSH port" -DefaultValue "$Port"
    try { $Port = [int]$portValue } catch { Write-Warning "Invalid port; using 22."; $Port = 22 }
}
if (-not $PSBoundParameters.ContainsKey('Timeout')) {
    $timeoutValue = Get-InputValue -Prompt "Timeout (seconds)" -DefaultValue "$Timeout"
    try { $Timeout = [int]$timeoutValue } catch { Write-Warning "Invalid timeout; using 15."; $Timeout = 15 }
}
if (-not $PSBoundParameters.ContainsKey('HostKeyPolicy')) {
    $HostKeyPolicy = Get-InputValue -Prompt "Host key policy (auto/reject/warning)" -DefaultValue $HostKeyPolicy
}
if (-not $KnownHosts) {
    $KnownHosts = Get-InputValue -Prompt "Known_hosts file path (blank = none)"
}

# Build the runtime device inventory.
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("devices:")
$lines.Add("  - name: interactive-device")
$lines.Add("    hostname: " + (ConvertTo-YamlStr $TargetHost))
$lines.Add("    vendor: $Vendor")
$lines.Add("    port: $Port")
$lines.Add("    username: " + (ConvertTo-YamlStr $Username))
$lines.Add("    password: " + (ConvertTo-YamlStr $Password))
$lines.Add("    timeout: $Timeout")
$lines.Add("    host_key_policy: $HostKeyPolicy")
if ($KnownHosts) { $lines.Add("    known_hosts: " + (ConvertTo-YamlStr $KnownHosts)) }

$configPath = Join-Path $PWD "config\interactive_devices.yml"
$dir = Split-Path -Parent $configPath
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
Set-Content -Path $configPath -Value ($lines -join "`n") -Encoding UTF8

# Auto-detect the backend profile unless explicitly overridden.
if ($ParamikoProfile -eq 'modern' -or $ParamikoProfile -eq 'legacy') {
    Write-Host "(SSH profile forced to '$ParamikoProfile' via -ParamikoProfile)"
}
else {
    Ensure-Venv -VenvDir '.venv' -RequirementsFile 'requirements.txt'
    Ensure-Venv -VenvDir '.venv-legacy' -RequirementsFile 'requirements-legacy.txt'
    Write-Host "Probing $TargetHost to auto-detect SSH profile (modern/legacy) ..."
    $probeOut = @(& ".venv\Scripts\python.exe" -m app.cli --config $configPath --probe 2>$null)
    $probeText = ($probeOut -join "`n")
    $class = "unreachable"
    try {
        $probeResults = $probeText | ConvertFrom-Json
        $class = if ($probeResults -is [array]) { $probeResults[0].classification } else { $probeResults.classification }
    }
    catch {
        Write-Warning "Could not parse probe output; defaulting to the modern profile."
    }

    if ($class -eq 'legacy') {
        $ParamikoProfile = 'legacy'
        Write-Host "Auto-detected a legacy SSH peer (older KEX/SHA-1 style handshake) - using the legacy Paramiko profile."
    }
    elseif ($class -eq 'modern') {
        $ParamikoProfile = 'modern'
        Write-Host "Auto-detected a modern SSH peer - using the standard Paramiko profile."
    }
    else {
        $ParamikoProfile = 'modern'
        Write-Warning "Probe could not reach $TargetHost for a non-legacy reason (host may be unreachable / auth / permission). The bootstrap will use the modern profile and record the failure."
    }
}

if ($ParamikoProfile -eq 'legacy') {
    Ensure-Venv -VenvDir '.venv-legacy' -RequirementsFile 'requirements-legacy.txt'
}
else {
    Ensure-Venv -VenvDir '.venv' -RequirementsFile 'requirements.txt'
}

$venvDir = if ($ParamikoProfile -eq 'legacy') { '.venv-legacy' } else { '.venv' }
Write-Host "Using profile: $ParamikoProfile  |  venv: $venvDir"
Write-Host ""
Write-Host "Collecting from $TargetHost using profile '$ParamikoProfile' ..."
$cliArgs = @("--config", $configPath, "--output-dir", $OutputDir)
if ($Verbose) { $cliArgs += "--verbose" }
& "$venvDir\Scripts\python.exe" -m app.cli @cliArgs

Write-Host ""
Write-Host "Done. Output is in: $PWD\$OutputDir"
Write-Host "Re-run with: & '$venvDir\Scripts\python.exe' -m app.cli --config '$configPath' --output-dir '$OutputDir'"
