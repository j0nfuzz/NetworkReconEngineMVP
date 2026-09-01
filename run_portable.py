"""Entry point for the PyInstaller-packaged CLI executable."""
from app.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
