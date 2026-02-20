param(
    [string]$Version = "0.1.0",
    [string]$Message = "Release $Version",
    [switch]$CreateGitHubRelease
n)

Write-Host "Preparing release $Version"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is not available in PATH. Install git to continue."
    exit 1
}

# Create annotated tag
git tag -a "v$Version" -m "$Message"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create git tag v$Version"
    exit $LASTEXITCODE
}

Write-Host "Pushing tag v$Version to origin"
git push origin "refs/tags/v$Version"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to push tag to origin"
    exit $LASTEXITCODE
}

if ($CreateGitHubRelease) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Error "GitHub CLI (gh) not found; cannot create GitHub release. Install gh or omit -CreateGitHubRelease."
        exit 1
    }

    $changelog = Get-Content -Path "CHANGELOG.md" -Raw
    $notes = "Release v$Version`n`n"
    # Try to extract the section for this version
    $pattern = "## \[${Version}\](.*?)(?=^## \[|\z)"
    $match = [regex]::Match($changelog, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline -bor [System.Text.RegularExpressions.RegexOptions]::Multiline)
    if ($match.Success) { $notes = $notes + $match.Groups[1].Value.Trim() }

    gh release create "v$Version" --title "v$Version" --notes "$notes"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create GitHub release via gh CLI"
        exit $LASTEXITCODE
    }
    Write-Host "GitHub release v$Version created"
}

Write-Host "Release process complete."
++++++++______