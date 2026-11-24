@echo off
title SDCRAFT - Playit.gg Free Multiplayer Tunnel
cls
echo =====================================================================
echo       SDCRAFT MINECRAFT - PLAYIT.GG FREE PUBLIC TUNNEL
echo =====================================================================
echo.
echo Launching Playit tunnel...
echo (If this is your first time, open the claim link displayed below)
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "tools\run_playit_windows.py"
) else (
    python "tools\run_playit_windows.py"
)

pause
