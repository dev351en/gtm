@echo off
title SDCRAFT - Connect to Daytona Cloud Server
cls
echo =====================================================================
echo          SDCRAFT MINECRAFT - DAYTONA CLOUD 24/7 HOSTING
echo =====================================================================
echo.
echo Launching secure connection to Daytona Cloud VPS...
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "tools\daytona_tunnel.py"
) else (
    python "tools\daytona_tunnel.py"
)

pause
