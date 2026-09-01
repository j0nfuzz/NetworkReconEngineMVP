PHASE:
EngineerLaunchExperience

STATUS:
Implemented

FILES MODIFIED:
- app/cli.py
  - Added _prompt_interactive_inventory() to gather hostname/IP, username, hidden password, port (default 22), and vendor (default auto).
  - Made --config optional (default None).
  - When --config is omitted, writes a temporary runtime YAML to output_dir/interactive_devices.yml and feeds it through the existing load_devices() / collection path.
  - Recursive CLI helper now receives the resolved config path so interactive runs work with --recursive.
- README.md
  - Added "Option 1: interactive launch" section describing prompt-based startup without an inventory file.
  - Updated portable distribution section with interactive packaged launch example.
- docs/HOWTO-PORTABLE.md
  - Documented interactive packaged launch flow (extract -> launch -> enter details -> collect).
  - Retained existing --config packaged workflow instructions.
- tests/test_cli.py
  - Added test_parse_args_config_is_optional.
  - Added test_prompt_interactive_inventory_writes_valid_yaml.
  - Added test_prompt_interactive_inventory_defaults_port_and_vendor.
  - Added test_prompt_interactive_inventory_password_not_echoed.

FILES ADDED:
- docs/Phases/IMPLEMENTED-PHASE-022-EngineerLaunchExperience.md

VALIDATION EVIDENCE:
- tests/test_cli.py: 59 passed (previously 55; 4 new tests added).
- Existing --config CLI tests continue to pass unchanged.
- get_errors reported no errors in app/cli.py or tests/test_cli.py.

TESTS ADDED:
- test_parse_args_config_is_optional
- test_prompt_interactive_inventory_writes_valid_yaml
- test_prompt_interactive_inventory_defaults_port_and_vendor
- test_prompt_interactive_inventory_password_not_echoed

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- Interactive prompts may not behave well in non-TTY environments; automated use should continue to use --config.
- Runtime inventory YAML is written to the output directory; the file should not be distributed.
- getpass may fall back to plain input in unusual console environments; standard Windows console and PyInstaller console builds support hidden password entry.

RISKS RESOLVED:
- Technicians no longer need to author a YAML inventory to perform a single-device collection.
- Packaged executable is now usable without carrying a pre-written config file.

OPEN ISSUES:
- Multi-device interactive entry is not implemented; phase scope remains single-device per prompt.
- --max-concurrent ceiling remains non-configurable (carried from PHASE-019).
