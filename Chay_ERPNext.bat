@echo off
chcp 65001 >nul
title Khoi dong ERPNext

echo ========================================================
echo           DANG KHOI DONG HE THONG ERPNEXT
echo ========================================================
echo.

cd /d "%~dp0frappe_docker"

echo [1/2] Dang khoi chay cac container ERPNext...
docker compose -f pwd.yml up -d

if %errorlevel% neq 0 (
    echo.
    echo [LOI] Khong the khoi dong cac container.
    echo Vui long kiem tra xem Docker Desktop da duoc bat hay chua!
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] Dang cho he thong web san sang...
timeout /t 5 >nul

echo.
echo ========================================================
echo   ERPNext da san sang!
echo   - Dia chi web:   http://localhost:8080
echo   - Tai khoan:     Administrator
echo   - Mat khau:      admin
echo ========================================================
echo.
echo Dang mo trinh duyet...
start http://localhost:8080
echo.
pause

