@echo off
title Audit Sistem Windows 7 - Koperasi Brimob
color 0A
echo ======================================================
echo    DIAGNOSIS SISTEM UNTUK APLIKASI KOPERASI BRIMOB
echo ======================================================
echo.

:: 1. Mengecek Versi Service Pack (Akar Sistem)
echo [1/3] Memeriksa Build Windows dan Service Pack...
systeminfo | findstr /B /C:"OS Version" > version_info.txt
for /f "tokens=3,4,5,6" %%a in (version_info.txt) do set build=%%a %%b %%c %%d
del version_info.txt

echo Versi Terdeteksi: %build%
echo %build% | find "7601" >nul
if %errorlevel%==0 (
    echo [OK] Service Pack 1 sudah terinstal. Lanjut ke update berikutnya.
) else (
    echo [PENTING] Service Pack 1 (KB976932) BELUM TERINSTAL!
    echo Silakan instal file di Folder 01_Service_Pack_1 terlebih dahulu.
)
echo.

:: 2. Mengecek KB Update Spesifik yang Hilang
echo [2/3] Memeriksa Daftar Update (KB) yang Dibutuhkan...
echo.

set missing_count=0
set updates=KB3020369 KB4490628 KB4474419 KB2999226

for %%i in (%updates%) do (
    wmic qfe get hotfixid | findstr "%%i" >nul
    if %errorlevel%==0 (
        echo [OK] %%i sudah terpasang.
    ) else (
        echo [!!] %%i MISSING (Belum Terinstal).
        set /a missing_count+=1
    )
)

echo.
echo ------------------------------------------------------
if %missing_count%==0 (
    echo HASIL: Sistem sudah SIAP menjalankan aplikasi!
) else (
    echo HASIL: Ada %missing_count% update yang harus diinstal manual dari USB.
)
echo ------------------------------------------------------
echo.

:: 3. Tombol Darurat Stop Update Service
echo [3/3] TIPS: Jika instalasi .msu macet (stuck), tekan 'S' 
echo       untuk mematikan layanan Windows Update sementara.
echo.
set /p action="Tekan ENTER untuk keluar atau 'S' untuk stop service: "
if /I "%action%"=="S" (
    echo Mematikan layanan wuauserv...
    net stop wuauserv
    echo.
    echo Sekarang coba jalankan kembali file .msu dari USB.
    pause
)

exit