# Run from the ANAVO repository in a terminal with network and Git write access.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
function Assert-CommandSucceeded([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE). Fix the error before continuing." }
}
# GitHub comes first and can publish honest blocked-status work independently of quantum setup.
python -m scripts.github_setup
Assert-CommandSucceeded 'GitHub connection, public anavo repository, commit and verified push'
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    python -m venv .venv
    Assert-CommandSucceeded 'Virtual environment creation'
}
$AnavoPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
& $AnavoPython -m pip --version
if ($LASTEXITCODE -ne 0) {
    python -m pip --python $AnavoPython install pip
    Assert-CommandSucceeded 'pip bootstrap'
}
& $AnavoPython -m pip install -r requirements.txt
Assert-CommandSucceeded 'Dependency installation'
& $AnavoPython -m unittest discover -s tests -v
Assert-CommandSucceeded 'Automated tests'
& $AnavoPython -m scripts.api_startup_check
Assert-CommandSucceeded 'FastAPI localhost startup'
& $AnavoPython -m scripts.benchmark --require-quantum
Assert-CommandSucceeded 'Real quantum benchmarks'
# The first commit is created after tests and actual benchmarks succeed.
git add -- .gitignore .streamlit PLAN.md TASKS.md README.md requirements.txt app.py backend src tests scripts docs results
Assert-CommandSucceeded 'Git staging'
git diff --cached --quiet
if ($LASTEXITCODE -eq 1) {
    git commit -m 'feat: implement and validate Anavo energy optimization prototype'
    Assert-CommandSucceeded 'Git commit'
} elseif ($LASTEXITCODE -ne 0) {
    throw 'Could not inspect staged changes'
}
& $AnavoPython -m scripts.verify_release
Assert-CommandSucceeded 'Strict release verification'
& $AnavoPython -m scripts.github_setup
Assert-CommandSucceeded 'Validated milestone push and remote verification'
Write-Output 'Review docs/REPORT.md, docs/PITCH.md, and TASKS.md against the new benchmark results before submission.'
