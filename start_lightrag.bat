@echo off
echo ========================================
echo Starting LightRAG Server
echo ========================================

cd /d "%~dp0LightRAG"
set PATH=%USERPROFILE%\.local\bin;%PATH%
set PYTHONIOENCODING=utf-8

echo.
echo Server will start at: http://127.0.0.1:9621
echo Web UI: http://127.0.0.1:9621
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

lightrag-server --host 127.0.0.1 --port 9621

pause