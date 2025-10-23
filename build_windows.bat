@echo off
REM Build a standalone Windows .exe with PyInstaller
REM Usage: double-click this or run in terminal (after installing requirements)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

REM --noconsole hides the console window; remove if you want logs
pyinstaller --noconsole --onefile --name KickPitchDetector --add-data "" ";." app.py

echo.
echo Build finished. Look in the "dist" folder for KickPitchDetector.exe
pause
