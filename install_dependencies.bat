@echo off

REM Check if python is installed
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Downloading and installing Python...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe -OutFile python-installer.exe"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
) else (
    echo Python is already installed.
)

REM Check if pip is installed
where pip >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo pip not found. Installing pip...
    python -m ensurepip
) else (
    echo pip is already installed.
)

REM Install dependencies if requirements.txt exists
IF EXIST requirements.txt (
    echo Checking for missing dependencies...
    pip install --upgrade --no-input --requirement requirements.txt
)

pause