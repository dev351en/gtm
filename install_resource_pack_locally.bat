@echo off
title SDCRAFT - Local Resource Pack Installer
cls
echo =====================================================================
echo           SDCRAFT - 1-CLICK RESOURCE PACK INSTALLER
echo =====================================================================
echo.
echo Installing EXPECT_SDCRAFT_ResourcePack_26.3.zip into your Minecraft folder...
echo.

set "SOURCE=github_gtm_repo\resource-pack\EXPECT_SDCRAFT_ResourcePack_26.3.zip"
set "DEST=%APPDATA%\.minecraft\resourcepacks"

if not exist "%DEST%" (
    mkdir "%DEST%"
)

if exist "%SOURCE%" (
    copy /Y "%SOURCE%" "%DEST%\EXPECT_SDCRAFT_ResourcePack_26.3.zip"
    echo [SUCCESS] Resource pack installed successfully into:
    echo           %DEST%\EXPECT_SDCRAFT_ResourcePack_26.3.zip
    echo.
    echo In Minecraft:
    echo   1. Go to Options -^> Resource Packs...
    echo   2. Move "SD Craft 26.3 SMP | 3D Vehicles" to the Selected (Right) side!
    echo   3. Click Done!
) else (
    echo [ERROR] Could not find %SOURCE%!
)

echo.
pause
