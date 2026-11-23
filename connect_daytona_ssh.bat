@echo off
title SDCRAFT - Daytona Cloud SSH Shell
cls
echo =====================================================================
echo                SDCRAFT - DAYTONA VPS LINUX TERMINAL
echo =====================================================================
echo.
echo Opening interactive SSH session into Daytona Cloud container...
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "tools\daytona_ssh_shell.py"
) else (
    python "tools\daytona_ssh_shell.py"
)

pause
