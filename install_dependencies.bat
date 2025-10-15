@echo off

REM Check if python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Downloading and installing Python...
    REM Download Python installer
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe -OutFile python-installer.exe"
    REM Install Python silently
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
) else (
    echo Python is already installed.
)

REM Install dependencies
pip install country_bounding_boxes matplotlib cartopy shapely
pause