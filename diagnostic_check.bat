@echo off
setlocal EnableDelayedExpansion
title System Diagnostic Tool - Koperasi Brimob

echo ========================================================
echo   Koperasi Brimob - System Diagnostic ^& Repair Tool
echo ========================================================
echo.
echo This tool will check your system for compatibility issues.
echo Supported OS: Windows 7, 8, 10, 11
echo.

set "LOGFILE=%~dp0sys_audit.txt"
echo [LOG] Diagnostic started at %date% %time% > "!LOGFILE!"

:: 1. OS Check
echo [1/4] Checking Operating System...
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo    OS Version: !VERSION!
echo [INFO] OS Version: !VERSION! >> "!LOGFILE!"

:: Check Architecture
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set ARCH=32-bit || set ARCH=64-bit
echo    Architecture: !ARCH!
echo [INFO] Architecture: !ARCH! >> "!LOGFILE!"

:: 2. Service Pack Check (Win 7 Only)
echo.
echo [2/4] Checking Service Pack...
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" >> "!LOGFILE!"
systeminfo | find "Service Pack 1" > NUL
if %errorlevel% equ 0 (
    echo    [OK] Service Pack 1 found (or not required).
    echo [OK] SP1 Found >> "!LOGFILE!"
) else (
    echo "!VERSION!" | find "6.1" > NUL
    if !errorlevel! equ 0 (
        echo    [!] WARNING: Windows 7 Service Pack 1 appears to be MISSING.
        echo    This application requires SP1 on Windows 7.
        echo [WARN] Win7 SP1 Missing >> "!LOGFILE!"
    ) else (
        echo    [OK] Not Windows 7, SP1 check skipped.
    )
)

:: 3. Windows Update Service Check
echo.
echo [3/4] Checking Windows Update Service...
sc query wuauserv | find "STATE" | find "RUNNING" > NUL
if %errorlevel% equ 0 (
    echo    [OK] Windows Update service is running.
    echo [OK] wuauserv Running >> "!LOGFILE!"
) else (
    echo    [!] Windows Update service is NOT running. Attempting to start...
    echo [WARN] wuauserv Stopped >> "!LOGFILE!"
    net start wuauserv
    if %errorlevel% equ 0 (
        echo    [OK] Service started successfully.
        echo [FIX] wuauserv Started >> "!LOGFILE!"
    ) else (
        echo    [ERROR] Failed to start Windows Update service. Run as Administrator.
        echo [FAIL] wuauserv Start Failed >> "!LOGFILE!"
    )
)

:: 4. Critical KB Check
echo.
echo [4/4] Checking Critical Updates...
echo    Scanning installed updates (this may take a moment)...

set "MISSING_KBS="

:: KB2533623 (Secure LoadLibrary - Critical for WinError 87)
wmic qfe get HotFixID | find "KB2533623" > NUL
if %errorlevel% equ 0 (
    echo    [OK] KB2533623 found.
    echo [OK] KB2533623 >> "!LOGFILE!"
) else (
    echo    [X] KB2533623 MISSING (Secure LoadLibrary - Fixes WinError 87 crash)
    set "MISSING_KBS=1"
    echo [MISSING] KB2533623 >> "!LOGFILE!"
)

:: KB3020369 (Servicing Stack)
wmic qfe get HotFixID | find "KB3020369" > NUL
if %errorlevel% equ 0 (
    echo    [OK] KB3020369 found.
    echo [OK] KB3020369 >> "!LOGFILE!"
) else (
    echo    [X] KB3020369 MISSING (Servicing Stack)
    set "MISSING_KBS=1"
    echo [MISSING] KB3020369 >> "!LOGFILE!"
)

:: KB4474419 (SHA-2)
wmic qfe get HotFixID | find "KB4474419" > NUL
if %errorlevel% equ 0 (
    echo    [OK] KB4474419 found.
    echo [OK] KB4474419 >> "!LOGFILE!"
) else (
    echo    [X] KB4474419 MISSING (SHA-2 Support)
    set "MISSING_KBS=1"
    echo [MISSING] KB4474419 >> "!LOGFILE!"
)

:: KB2999226 (UCRT)
wmic qfe get HotFixID | find "KB2999226" > NUL
if %errorlevel% equ 0 (
    echo    [OK] KB2999226 found.
    echo [OK] KB2999226 >> "!LOGFILE!"
) else (
    echo    [X] KB2999226 MISSING (Universal C Runtime)
    set "MISSING_KBS=1"
    echo [MISSING] KB2999226 >> "!LOGFILE!"
)

echo.
echo ========================================================
if defined MISSING_KBS (
    echo [ATTENTION] Some critical updates are missing!
    echo The application may not run correctly.
    echo Check sys_audit.txt for details.
    echo.
    echo Please install the missing updates listed above.
) else (
    echo [SUCCESS] All system checks passed.
    echo Your system is ready for Koperasi Brimob.
)
echo ========================================================

pause
