@echo off
chcp 65001 >nul
set LOGFILE=C:\Users\Qiu\Downloads\calendar option\logs\sp500_%date:~0,4%%date:~5,2%%date:~8,2%.txt
"C:\Users\Qiu\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\Qiu\Downloads\calendar option\sp500_scanner.py" > "%LOGFILE%" 2>&1
