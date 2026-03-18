@echo off
chcp 65001 >nul
for /f "tokens=*" %%i in ('powershell -Command "Get-Date -Format yyyyMMdd"') do set TODAY=%%i
set LOGFILE=C:\Users\Qiu\Downloads\calendar option\logs\sp500_earnings_%TODAY%.txt
"C:\Users\Qiu\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\Qiu\Downloads\calendar option\sp500_earning_scanner.py" > "%LOGFILE%" 2>&1
