<#
Push the current project to GitHub and (optionally) set SENTRY_DSN as a secret.

Usage:
  .\push_to_github.ps1 [--RepoName name] [--Visibility public|private]

Behavior:
- Initializes git if needed
- Makes an initial commit if there are uncommitted changes
- Creates a GitHub repo via `gh` if available (preferred), or asks for a remote URL
- Pushes `main` branch and sets `origin`
- If `SENTRY_DSN` is present in the environment and `gh` is available, sets it as a repo secret
#>

param(
    [string]$RepoName = $(Read-Host 'Enter GitHub repo name (leave blank to use current folder name)'),
    [ValidateSet('public','private')][string]$Visibility = 'public'
)

function RunCmd([string]$cmd, [switch]$exitOnFail) {
    Write-Host "> $cmd"
    $process = Start-Process -FilePath pwsh -ArgumentList "-NoProfile","-Command","$cmd" -Wait -PassThru -NoNewWindow
    if ($process.ExitCode -ne 0) {
        Write-Error "Command failed: $cmd (exit $($process.ExitCode))"
        if ($exitOnFail) { exit $process.ExitCode }
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not available in PATH. Install Git and rerun this script."
    exit 1
}

$cwd = Split-Path -Leaf (Get-Location)
if (-not $RepoName -or $RepoName -eq '') { $RepoName = $cwd }

if (-not (Test-Path .git)) {
    Write-Host 'Initializing git repository...'
    RunCmd 'git init' -exitOnFail
}

$status = (git status --porcelain) -join "`n"
if ($status) {
    Write-Host 'Staging and committing changes...'
    RunCmd 'git add -A' -exitOnFail
    $msg = Read-Host 'Commit message (default: "Initial commit")'
    if (-not $msg) { $msg = 'Initial commit' }
    RunCmd "git commit -m \"$msg\"" -exitOnFail
} else {
    Write-Host 'No changes to commit.'
}

# Ensure branch name is main
try { git rev-parse --abbrev-ref HEAD > $null 2>&1; $current = (git rev-parse --abbrev-ref HEAD).Trim() } catch { $current = '' }
if ($current -and $current -ne 'main') {
    Write-Host "Current branch is '$current'. Renaming to 'main'..."
    RunCmd 'git branch -M main' -exitOnFail
} elseif (-not $current) {
    RunCmd 'git branch -M main' -exitOnFail
}

# prefer GitHub CLI if available
$ghAvailable = $false
if (Get-Command gh -ErrorAction SilentlyContinue) { $ghAvailable = $true }

if ($ghAvailable) {
    Write-Host "Using GitHub CLI to create/push repo '$RepoName' ($Visibility)"
    # Create repo (will fail if exists; gh will set remote and push when --source and --push used)
    $createCmd = "gh repo create $RepoName --$Visibility --source=. --remote=origin --push"
    RunCmd $createCmd -exitOnFail

    if ($env:SENTRY_DSN) {
        Write-Host 'Setting SENTRY_DSN secret in the repository (via gh)...'
        $tmp = [System.IO.Path]::GetTempFileName()
        Set-Content -Path $tmp -Value $env:SENTRY_DSN -NoNewline
        RunCmd "gh secret set SENTRY_DSN --body `"$([System.IO.File]::ReadAllText($tmp))`"" -exitOnFail
        Remove-Item $tmp -ErrorAction SilentlyContinue
    }
} else {
    Write-Host 'GitHub CLI (`gh`) not found. Falling back to manual remote setup.'
    # If origin already exists, show and confirm
    $origin = ''
    try { $origin = (git remote get-url origin) -join "`n" } catch { $origin = '' }
    if ($origin) {
        Write-Host "Found existing origin: $origin"
        $useExisting = Read-Host 'Use existing origin? (Y/n)'
        if ($useExisting -and $useExisting -match '^[nN]') {
            $remote = Read-Host 'Enter new remote Git URL (e.g. https://github.com/you/repo.git)'
            if (-not $remote) { Write-Error 'Remote URL required. Exiting.'; exit 1 }
            RunCmd "git remote set-url origin $remote" -exitOnFail
        }
    } else {
        $remote = Read-Host 'Enter remote Git URL (e.g. https://github.com/you/repo.git)'
        if (-not $remote) { Write-Error 'Remote URL required. Exiting.'; exit 1 }
        RunCmd "git remote add origin $remote" -exitOnFail
    }

    RunCmd 'git push -u origin main' -exitOnFail
}

Write-Host 'Done. Visit your GitHub repository to verify CI runs under Actions.'
