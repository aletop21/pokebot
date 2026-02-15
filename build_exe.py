"""Build a Windows .exe for the GUI bot using PyInstaller.

Usage:
    python build_exe.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "tibia_pokebot_auto"
ENTRYPOINT = "gui_auto.py"


def main() -> int:
    if not Path(ENTRYPOINT).exists():
        print(f"Entrypoint not found: {ENTRYPOINT}")
        return 1

    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller is None:
        print("PyInstaller is not installed.")
        print("Install it with: python -m pip install pyinstaller")
        return 2

    cmd = [
        pyinstaller,
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        ENTRYPOINT,
    ]

    print("Running:", " ".join(cmd))
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        return completed.returncode

    dist_path = Path("dist") / f"{APP_NAME}.exe"
    if dist_path.exists():
        print(f"Build complete: {dist_path}")
    else:
        print("Build finished, but .exe was not found. Check dist/ folder output for your OS.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
