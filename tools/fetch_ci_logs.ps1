<#
Fetch GitHub Actions run logs using the GitHub CLI (`gh`).

Usage:
  .\tools\fetch_ci_logs.ps1 --run <run-id>            # numeric run id
  .\tools\fetch_ci_logs.ps1 --url <run-url>           # full Actions run URL

The script will display the run summary and stream logs (requires gh authenticated).
#>

param(
    [string]$RunId,
    [string]$Url
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI 'gh' not found. Install and authenticate (gh auth login) to use this script."
    exit 1
}

if (-not $RunId -and -not $Url) {
    Write-Host "Provide either --run <run-id> or --url <run-url>."
    exit 1
}

if ($Url) {
    # extract run id from URL if possible
    $m = [regex]::Match($Url, '/runs/(\d+)')
    if ($m.Success) { $RunId = $m.Groups[1].Value }
}

Write-Host "Fetching run summary for run id: $RunId"
gh run view $RunId --log || {
    Write-Error "Failed to fetch run logs for $RunId"
    exit 1
}

Write-Host "Logs streamed. You can also download the full logs using: gh run download $RunId --logs"
