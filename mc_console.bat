@echo off
title SDCRAFT - Minecraft Live Console
cls
echo =====================================================================
echo                 SDCRAFT MINECRAFT LIVE CONSOLE
echo =====================================================================
echo.
echo Type Minecraft commands below (e.g. op, whitelist, say, save-all, plugins)
echo Type 'exit' to quit.
echo =====================================================================
echo.

:loop
set /p cmd="[MC CONSOLE]> "
if /i "%cmd%"=="exit" goto end
if "%cmd%"=="" goto loop

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "tools\daytona_mc_cmd.py" "%cmd%"
) else (
    python "tools\daytona_mc_cmd.py" "%cmd%"
)

echo.
goto loop

:end
echo Exiting console.
pause
