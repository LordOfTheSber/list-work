@echo off
setlocal

REM Сборка Windows exe через PyInstaller
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --onefile --windowed --name fuel_logs_app fuel_logs/main.py

echo.
echo Готово. Файл: dist\fuel_logs_app.exe
endlocal
