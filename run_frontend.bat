@echo off
chcp 65001 >nul
echo ===================================================
echo [Customer 360] Starting Node.js Frontend Server...
echo ===================================================
cd customer360-frontend
node server.js
pause
