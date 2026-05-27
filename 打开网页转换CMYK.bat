@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

if not exist "src\web_app.py" (
    echo Missing script: src\web_app.py
    pause
    exit /b 1
)

set "PYTHON_CMD="

py -3 --version >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"

if "%PYTHON_CMD%"=="" (
    python --version >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
    echo Python was not found.
    echo Please install Python 3.10 or newer, and enable "Add Python to PATH".
    echo Download: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo Pillow was not found.
    echo Trying to install it automatically. Please keep the network connected...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Pillow installation failed.
        echo Please open Command Prompt in this folder and run:
        echo %PYTHON_CMD% -m pip install -r requirements.txt
        pause
        exit /b 1
    )
)

%PYTHON_CMD% "src\web_app.py"
echo.
pause
