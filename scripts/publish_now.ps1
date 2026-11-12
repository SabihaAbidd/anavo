# Publish existing ANAVO work immediately using Git and its configured credential manager.
# Run in ordinary Windows PowerShell, outside the ChatGPT managed execution session.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

function Assert-AnavoGit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (Git exit $LASTEXITCODE). No force/reset/lock deletion was attempted." }
}

$AnavoBranch = git branch --show-current
Assert-AnavoGit 'Branch inspection'
if ($AnavoBranch.Trim() -ne 'main') { throw 'Select the intended main branch first; this script will not rewrite branches.' }

$AnavoAllowedOrigins = @('https://github.com/SabihaAbidd/anavo.git', 'https://github.com/SabihaAbidd/anavo', 'git@github.com:SabihaAbidd/anavo.git')
$AnavoRemotes = @(git remote)
Assert-AnavoGit 'Remote inspection'
if ($AnavoRemotes -contains 'origin') {
    $AnavoOrigin = git remote get-url origin
    Assert-AnavoGit 'Origin inspection'
    if ($AnavoAllowedOrigins -notcontains $AnavoOrigin.Trim()) { throw 'Origin points elsewhere. Refusing to replace it.' }
} else {
    git remote add origin 'https://github.com/SabihaAbidd/anavo.git'
    Assert-AnavoGit 'Origin configuration'
}

$AnavoRemoteHeads = @(git ls-remote --heads origin)
Assert-AnavoGit 'Remote branch inspection'
$AnavoOldHead = git rev-parse --verify --quiet HEAD
$AnavoHasCommit = ($LASTEXITCODE -eq 0)
if ($AnavoRemoteHeads.Count -gt 0) {
    if (-not $AnavoHasCommit) { throw 'Remote already has history but this checkout has no commits. Preserve both; clone the repository to a new folder instead of overwriting history.' }
    if (-not ($AnavoRemoteHeads | Where-Object { $_ -match '\srefs/heads/main$' })) { throw 'Remote has other history but no main; inspect it before publishing.' }
    git fetch --no-tags origin main
    Assert-AnavoGit 'Remote history fetch'
    git merge-base --is-ancestor FETCH_HEAD HEAD
    Assert-AnavoGit 'History compatibility check'
}

git add -- .gitignore .github .streamlit AGENTS.md PLAN.md TASKS.md README.md requirements.txt app.py backend src tests scripts docs results
Assert-AnavoGit 'Staging project files'
$AnavoStagedPaths = @(git diff --cached --name-only)
Assert-AnavoGit 'Staged-file inspection'
foreach ($AnavoStagedPath in $AnavoStagedPaths) {
    if ($AnavoStagedPath -notmatch '^(\.gitignore|AGENTS\.md|PLAN\.md|TASKS\.md|README\.md|requirements\.txt|app\.py)$|^(\.github|\.streamlit|backend|src|tests|scripts|docs|results)/') {
        throw "Unexpected staged path: $AnavoStagedPath. Review it manually before committing."
    }
    git check-ignore --no-index --quiet -- $AnavoStagedPath
    if ($LASTEXITCODE -eq 0) { throw "Ignored content is already staged: $AnavoStagedPath. Review it manually before committing." }
    if ($LASTEXITCODE -ne 1) { throw 'Could not inspect ignored-file status.' }
}

git diff --cached --quiet
if ($LASTEXITCODE -eq 1) {
    git commit -m 'feat: add Anavo optimization engine and FastAPI backend with validated contracts'
    Assert-AnavoGit 'Project commit'
} elseif ($LASTEXITCODE -ne 0) { throw 'Could not inspect staged changes.' }

$AnavoCommit = git rev-parse --verify HEAD
Assert-AnavoGit 'Commit verification'
Write-Output 'Publishing to GitHub. Complete the browser sign-in if Git Credential Manager opens it.'
git push --set-upstream origin main
Assert-AnavoGit 'GitHub push'

$AnavoRemoteLine = @(git ls-remote origin refs/heads/main)
Assert-AnavoGit 'Remote commit verification'
if ($AnavoRemoteLine.Count -ne 1) { throw 'Expected exactly one remote main ref.' }
$AnavoRemoteCommit = ($AnavoRemoteLine[0] -split '\s+')[0]
if ($AnavoRemoteCommit -ne $AnavoCommit.Trim()) { throw 'Local and remote main hashes differ.' }

git fetch --no-tags origin main
Assert-AnavoGit 'Published file verification fetch'
$AnavoFetchedCommit = git rev-parse FETCH_HEAD
Assert-AnavoGit 'Fetched commit verification'
if ($AnavoFetchedCommit.Trim() -ne $AnavoCommit.Trim()) { throw 'Fetched commit differs from the published commit.' }
$AnavoExpectedPaths = @('README.md', 'backend/main.py', 'src/quantum_solver.py')
$AnavoPublishedPaths = @(git ls-tree --name-only FETCH_HEAD -- @AnavoExpectedPaths)
Assert-AnavoGit 'Published file verification'
foreach ($AnavoExpectedPath in $AnavoExpectedPaths) {
    if ($AnavoPublishedPaths -notcontains $AnavoExpectedPath) { throw "Remote file missing: $AnavoExpectedPath" }
}

Write-Output ''
Write-Output 'VERIFIED: https://github.com/SabihaAbidd/anavo'
Write-Output 'Branch: main'
Write-Output "Commit: $($AnavoCommit.Trim())"
Write-Output 'Remote hash matches; README, backend and quantum implementation files are present.'
Write-Output 'Publishing does not mark the documented API/quantum dependency blockers as resolved.'
