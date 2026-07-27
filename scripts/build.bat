@echo off
chcp 65001 >nul
echo ============================================
echo   English Practice Tool - Build Script
echo ============================================
echo.

pip install pyinstaller -q 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller
    pause
    exit /b 1
)

echo [1/3] Cleaning previous build...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo [2/3] Building EXE with PyInstaller...
cd /d "%~dp0\.."
pyinstaller scripts\app.spec --noconfirm --clean

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo [3/3] Build complete!
echo.
echo Output: dist\EnglishPracticeTool\EnglishPracticeTool.exe
echo.
pause
