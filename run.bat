@echo off
python -c "import requests" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests library...
    python -m pip install requests
)
setlocal
cd /d %~dp0
call python tool.py
pause
