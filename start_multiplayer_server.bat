@echo off
title SDCRAFT - Daytona Cloud + Ngrok Multiplayer
cls
echo =====================================================================
echo        SDCRAFT MINECRAFT - DAYTONA CLOUD + NGROK MULTIPLAYER
echo =====================================================================
echo.
echo Connecting to Daytona Cloud (6.5 GB RAM, 64-core) and launching Ngrok...
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "tools\launch_daytona_and_ngrok.py"
) else (
    python "tools\launch_daytona_and_ngrok.py"
)

pause
