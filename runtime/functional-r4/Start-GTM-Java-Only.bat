@echo off
call "%~dp0Start-GTM.bat" --java-only %*
exit /b %ERRORLEVEL%
