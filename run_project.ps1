# Run this script in PowerShell to install dependencies for the current user and run the app without activating a virtualenv.
# Usage (PowerShell):
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\run_project.ps1

$ErrorActionPreference = 'Stop'
Write-Host "Installing required Python packages (user install)"
# Use pip for the user to avoid requiring admin rights. If pip is not found, instruct the user.
try {
    pip --version > $null 2>&1
} catch {
    Write-Host "Error: pip was not found on PATH. Please install Python and ensure pip is available." -ForegroundColor Red
    exit 1
}

# Install requirements for the current user
pip install --user -r .\requirements.txt

Write-Host "Starting the Flask app using system Python..."
# Run the Flask app
python .\code\main.py
