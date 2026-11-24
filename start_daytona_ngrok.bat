@echo off
title SDCRAFT - Start Daytona Ngrok Tunnel for Friends
cls
echo =====================================================================
echo       SDCRAFT MINECRAFT - START NGROK TCP TUNNEL ON DAYTONA
echo =====================================================================
echo.
echo Launching Ngrok tunnel on Daytona Cloud server...
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "tools\start_daytona_ngrok.py"
) else (
    python "tools\start_daytona_ngrok.py"
)

echo.
pause
