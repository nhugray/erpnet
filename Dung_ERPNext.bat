@echo off
chcp 65001 >nul
title Dung ERPNext

echo ========================================================
echo           DANG DUNG HE THONG ERPNEXT
echo ========================================================
echo.

cd /d "%~dp0frappe_docker"

echo Dang dung toan bo container ERPNext...
docker compose -f pwd.yml stop

echo.
echo ========================================================
echo   Da dung ERPNext thanh cong!
echo   * Cac container o trang thai Exited (da tat).
echo   * Khi ban mo Docker Desktop, ERPNext se KHONG tu bat.
echo   * Chi khi nao ban chay file "Chay_ERPNext.bat", no moi chay.
echo ========================================================
echo.
pause

