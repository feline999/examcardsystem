<#
Generate a locked requirements file from the active Python environment.

Usage:
  Activate your virtualenv, then run:
    .\tools\pin_requirements.ps1

Output:
  requirements-lock.txt
#>

try {
    python -V > $null 2>&1
} catch {
    Write-Error "Python not found in PATH. Activate your environment and retry."
    exit 1
}

Write-Host "Generating requirements-lock.txt from current environment..."
& python -m pip freeze | Out-File -Encoding utf8 requirements-lock.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to generate requirements-lock.txt"
    exit $LASTEXITCODE
}

Write-Host "Wrote requirements-lock.txt (commit this file for reproducible CI builds)."