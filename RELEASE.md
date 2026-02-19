# Release Checklist

Use this checklist to produce a release for the Exam Card System repository.

1. Ensure tests pass locally or in CI.

2. Update `CHANGELOG.md` with the new version section, e.g. `## [0.1.1] - YYYY-MM-DD`.

3. Create and push a signed/annotated tag locally (PowerShell):

```powershell
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin refs/tags/v0.1.0
```

4. Optionally create a GitHub Release using the helper (requires `gh`):

```powershell
# create a release (reads CHANGELOG.md for notes)
.\create_release.ps1 -Version 0.1.0 -CreateGitHubRelease
```

5. The repository includes a workflow `.github/workflows/release.yml` that will auto-create a GitHub Release when a tag matching `v*` is pushed. If you use the `create_release.ps1` helper with `-CreateGitHubRelease`, it will perform a similar operation via the `gh` CLI.

6. After release, update the `README.md` CI badge to reference your repository and consider adding a release badge.
