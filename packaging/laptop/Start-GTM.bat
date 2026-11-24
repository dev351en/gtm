@echo off
setlocal
cd /d "%~dp0"
title GTM - Local Laptop Candidate
set "GTM_JAVA=%~dp0runtime\java\bin\java.exe"
if exist "%GTM_JAVA%" goto launch
if defined JAVA_HOME set "GTM_JAVA=%JAVA_HOME%\bin\java.exe"
if exist "%GTM_JAVA%" goto launch
set "GTM_JAVA=java"
where java >nul 2>nul
if errorlevel 1 (
  echo Java 25 was not found. Install Java 25 or set JAVA_HOME to its installation folder.
  echo Official instructions: https://docs.papermc.io/misc/java-install/
  pause
  exit /b 1
)
:launch
"%GTM_JAVA%" --add-modules jdk.httpserver -jar "launcher\gtm-launcher.jar" %*
set "GTM_EXIT=%ERRORLEVEL%"
if not "%GTM_EXIT%"=="0" echo GTM stopped with exit code %GTM_EXIT%. Read the message above and logs\latest.log.
pause
exit /b %GTM_EXIT%
