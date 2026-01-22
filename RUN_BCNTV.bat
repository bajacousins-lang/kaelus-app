@echo off
title BCNTV Bot - Modo Servicio
cd /d "%~dp0"

echo ============================================
echo   BCNTV PLUS - INICIANDO SISTEMA SEGURO
echo ============================================

:: Verificamos si existe el archivo de secretos
if not exist .env (
    echo [!] ERROR: No se encontro el archivo .env
    pause
    exit
)

echo [%date% %time%] Lanzando bot.py desde ruta corregida...

:: EJECUCIÓN CON TU RUTA REAL
"C:\Users\Francisca\AppData\Local\Python\pythoncore-3.14-64\python.exe" bot.py

echo.
echo [!] El proceso se detuvo. Reiniciando en 5 segundos...
timeout /t 5