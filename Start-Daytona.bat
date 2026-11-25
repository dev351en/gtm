@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
call "%~dp0connect_daytona_server.bat" %*
exit /b %ERRORLEVEL%
