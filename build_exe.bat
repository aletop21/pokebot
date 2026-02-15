@echo off
setlocal

python build_exe.py
if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b %errorlevel%
)

echo.
echo Done. Check dist\tibia_pokebot_auto.exe
