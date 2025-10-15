# Check if python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Downloading and installing Python..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe" -OutFile "python-installer.exe"
    Start-Process -FilePath "python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item "python-installer.exe"
} else {
    Write-Host "Python is already installed."
}

# Refresh environment variables for current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Check if pip is installed
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "pip not found. Installing pip..."
    python -m ensurepip
} else {
    Write-Host "pip is already installed."
}

Write-Host "Checking for missing dependencies..."

# Read requirements.txt and install only missing packages
if (Test-Path "requirements.txt") {
    $requirements = Get-Content requirements.txt | Where-Object { $_ -and -not $_.StartsWith("#") }
    foreach ($pkg in $requirements) {
        $pkgName = $pkg.Split("==")[0]
        if (-not (python -m pip show $pkgName)) {
            Write-Host "Installing missing package: $pkg"
            pip install $pkg
        } else {
            Write-Host "$pkgName is already installed."
        }
    }
} else {
    Write-Host "requirements.txt not found."
}

Pause
