# Enhanced Tibia Pokemon Bot Flow

This project adds **real-time battlefield position tracking** on top of battle-window detection.

## Implemented capabilities

- Detects newly appeared pokemon from battle-window entries.
- Targets the **second pokemon** in battle list when a new entry appears.
- Sends configurable combat commands in sequence.
- Tracks each pokemon's last known battlefield coordinates during combat.
- When a pokemon disappears from battle list (defeated), throws the selected pokeball at the exact tracked coordinates.
- Supports per-pokemon pokeball selection, with a default fallback ball.
- Includes **hover-to-confirm mapping** in the GUI so you can move your mouse to a desired point and apply that exact coordinate to mapping fields.

## Main files

- `bot_engine_auto.py`: Core combat/capture automation state machine.
- `gui_auto.py`: Tkinter configuration UI for commands, hover-based mapping confirmation, and pokeball mapping.
- `tests/test_bot_engine_auto.py`: Unit tests for detect/track/throw behavior.
- `build_exe.py`: Build helper that packages the app into a Windows `.exe` using PyInstaller.
- `build_exe.bat`: Windows shortcut script to build the `.exe`.

## Quick run

```bash
python gui_auto.py
```

Then:
1. Configure commands (`m12,m11,...`).
2. Use the live mouse panel and **Use Hover** buttons to confirm ball positions.
3. Add optional pokemon-specific ball positions with each row's **Use Hover** button.
4. Press **Start** and run a demo tick.

## Build a Windows EXE

On a Windows machine:

```bat
python -m pip install pyinstaller
build_exe.bat
```

Expected output:

- `dist\tibia_pokebot_auto.exe`

Equivalent manual build command:

```bat
pyinstaller --noconfirm --clean --onefile --windowed --name tibia_pokebot_auto gui_auto.py
```

## Notes

The engine is input-library agnostic via `InputAdapter`, so you can connect it to your preferred automation stack (e.g., pyautogui) without changing combat logic.
