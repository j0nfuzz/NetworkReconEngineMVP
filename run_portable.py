"""Entry point for the packaged CLI executable and embedded runtime bundle."""
import sys
from pathlib import Path

# Ensure the bundle root is on sys.path when the embedded interpreter is used.
_bundle_root = Path(__file__).resolve().parent
if str(_bundle_root) not in sys.path:
    sys.path.insert(0, str(_bundle_root))

from app.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
