@echo off
chcp 65001 >nul
echo ===================================================
echo [Customer 360] Starting Python Backend API...
echo ===================================================
cd customer360-backend
python -m pip install -r requirements.txt
python run.py
pause
