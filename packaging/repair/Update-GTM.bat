@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "GTM_PAYLOAD=%~dp0"
set "GTM_INSTALLER=%GTM_PAYLOAD%install_runtime_repair.py"
set "GTM_INTERACTIVE=0"
if not exist "%GTM_INSTALLER%" set "GTM_INSTALLER=%GTM_PAYLOAD%tools\install_runtime_repair.py"
if not exist "%GTM_INSTALLER%" goto missing
if not exist "%GTM_PAYLOAD%repair-manifest.json" goto missing
set "GTM_SERVER=%~1"
if not "%GTM_SERVER%"=="" goto python
set "GTM_INTERACTIVE=1"
echo Stop the server and its launcher before applying this update.
echo Enter the folder containing server.properties and your existing worlds.
set /p "GTM_SERVER=Existing server folder: "
if "%GTM_SERVER%"=="" goto usage

:python
set "GTM_PYTHON=py -3"
py -3 -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if not errorlevel 1 goto run
set "GTM_PYTHON=python"
python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if not errorlevel 1 goto run
echo Python 3.10 or newer is required to run the verified updater.
set "GTM_RESULT=2"
goto finish

:run
if "%~2"=="--rollback" goto rollback
if not "%~3"=="" goto usage
if "%~2"=="--bedrock" goto bedrock
if not "%~2"=="" goto usage
%GTM_PYTHON% "%GTM_INSTALLER%" apply --payload "%GTM_PAYLOAD%." --server "%GTM_SERVER%"
set "GTM_RESULT=%ERRORLEVEL%"
goto finish

:bedrock
%GTM_PYTHON% "%GTM_INSTALLER%" apply --payload "%GTM_PAYLOAD%." --server "%GTM_SERVER%" --bedrock
set "GTM_RESULT=%ERRORLEVEL%"
goto finish

:rollback
if "%~3"=="" goto usage
if not "%~4"=="" goto usage
%GTM_PYTHON% "%GTM_INSTALLER%" rollback --server "%GTM_SERVER%" --backup "%~3"
set "GTM_RESULT=%ERRORLEVEL%"
goto finish

:missing
echo Extract the complete GTM repair package before running Update-GTM.bat.
set "GTM_RESULT=2"
goto finish

:usage
echo Usage: Update-GTM.bat "C:\path\to\existing\server" [--bedrock]
echo Undo:  Update-GTM.bat "C:\path\to\existing\server" --rollback BACKUP_ID
set "GTM_RESULT=2"

:finish
if "%GTM_INTERACTIVE%"=="1" pause
exit /b %GTM_RESULT%
