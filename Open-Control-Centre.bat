@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
title GTM - Private Control Centre
set "GTM_PY_ARGS="
set "GTM_PY=%~dp0.venv\Scripts\python.exe"
if exist "%GTM_PY%" goto run
set "GTM_PY=%~dp0..\.venv\Scripts\python.exe"
if exist "%GTM_PY%" goto run
python.exe -c "import sys" >nul 2>nul
if not errorlevel 1 (
 set "GTM_PY=python.exe"
 goto run
)
py.exe -3 -c "import sys" >nul 2>nul
if not errorlevel 1 (
 set "GTM_PY=py.exe"
 set "GTM_PY_ARGS=-3"
 goto run
)
echo Python 3.10 or newer is required to open the secure console connection.
pause
exit /b 1
:run
if exist "%~dp0plugins\SDCraftCore\console-access.token" (
 "%GTM_PY%" %GTM_PY_ARGS% "%~dp0tools\open_control_centre.py" --server "%~dp0." %*
) else (
 "%GTM_PY%" %GTM_PY_ARGS% "%~dp0tools\open_control_centre.py" --daytona --server "%~dp0." %*
)
set "GTM_EXIT=%ERRORLEVEL%"
if not "%GTM_EXIT%"=="0" pause
exit /b %GTM_EXIT%
