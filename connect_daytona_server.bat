@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
title GTM - Connect to Existing Daytona Server
set "GTM_PY_ARGS="
set "GTM_PY=%~dp0.venv\Scripts\python.exe"
if exist "%GTM_PY%" goto run
set "GTM_PY=%~dp0..\.venv\Scripts\python.exe"
if exist "%GTM_PY%" goto run
where python.exe >nul 2>nul
if not errorlevel 1 (
  python.exe -c "import sys" >nul 2>nul
  if not errorlevel 1 (
    set "GTM_PY=python.exe"
    goto run
  )
)
where py.exe >nul 2>nul
if not errorlevel 1 (
  py.exe -3 -c "import sys" >nul 2>nul
  if not errorlevel 1 (
    set "GTM_PY=py.exe"
    set "GTM_PY_ARGS=-3"
    goto run
  )
)
goto missing_python
:run
"%GTM_PY%" %GTM_PY_ARGS% "%~dp0tools\daytona_tunnel.py" %*
set "GTM_EXIT=%ERRORLEVEL%"
if not "%GTM_EXIT%"=="0" echo The connection did not complete. Read the message above.
pause
exit /b %GTM_EXIT%
:missing_python
echo Python 3.10 or newer was not found. This existing-Daytona connector uses Python and Windows OpenSSH.
echo Read docs\DAYTONA_LAPTOP_CONNECTION.md. Start-GTM-Java-Only.bat in the local playable ZIP is a separate launcher.
pause
exit /b 1
