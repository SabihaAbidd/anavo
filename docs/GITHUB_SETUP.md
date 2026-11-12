# GitHub setup and verification

Required destination: public repository **anavo**, description **Quantum-Assisted Energy Resilience Optimization for Pakistan**, owner equal to the authenticated user, default/submission branch **main**. No alternate name is created.

## Current observed state

**Update 2026-11-12:** remote main was verified at 3940efd61cdc3eaa7cba19abafe923709ff7a9b1, matching local HEAD. The blocker notes below are kept as history.

The GitHub integration is installed and authenticated as **SabihaAbidd**. Public **https://github.com/SabihaAbidd/anavo**, repository ID 1455287545, now contains the user-published project. Local origin/main and the remote were verified at d9c24703603b8f833b140cdd76338cd42d697b4e. This replaces earlier empty-repository observations. The project must not be recreated.

The first attempted `.gitignore` commit returned **403 Resource not accessible by integration**. User-level admin/push flags in repository metadata do not establish that the integration token can write contents. No remote commit/file write succeeded. Listing manageable GitHub App installations returned no entries, so no configurable installation was available through the integration. No account permissions were changed.

The later agent attempt to publish the numerical/validation/CI milestone through GitHub's Git-tree API also returned 403. The user's initial terminal publication remains verified; this separate new milestone is still unpublished. Run scripts/publish_now.ps1 from an ordinary terminal to publish it, then inspect the repository's Actions tab for an actual backend validation run. A locally parsed workflow file is not a completed run.

Local main and origin now exist. The user's ordinary PowerShell successfully committed/pushed the initial work; the managed agent session still cannot create `.git/index.lock` when staging. Its execution profile permits reading `.git` while denying required metadata writes. There is no stale lock to delete. Do not change ACLs, force-push, relocate Git metadata or bypass restrictions. User-run publication does not automatically grant this session write access.

## Repository access recovery when using the integration

The public repository now exists; **do not create another one**. Open https://github.com/settings/installations and inspect the ChatGPT/OpenAI GitHub App if listed. Its repository grant must include anavo, and publishing requires Contents write permission. If no such app/grant exists or the connector is read-only, use the local authenticated CLI recovery below. Integration installation, readable repository metadata and user push permission are not a successful content-write authorization. Do not paste credentials into chat.

## Safe local CLI recovery

### Immediate publication without installing GitHub CLI

Git is already installed with Git Credential Manager configured. In ordinary Windows PowerShell, from the project folder, run `.\scripts\publish_now.ps1`. This script uses only Git: it checks origin/history and ignore rules, commits intended project paths, pushes main, compares local/remote SHAs, fetches that commit and verifies expected remote files. Complete GitHub sign-in in the browser if Credential Manager opens it. It does not wait for Python, FastAPI, Qiskit, test installation, or GitHub CLI. Current dependency blockers remain honestly documented.

This ordinary terminal is necessary because the managed agent session itself denies Git metadata writes. Do not delete nonexistent lock files, modify ACLs or revoke unrelated apps.

Run in ordinary Windows PowerShell with network and Git write access:

```powershell
Set-Location -LiteralPath 'C:\path\to\Anavo'
winget install --id GitHub.cli --exact
```

After installation, open a fresh terminal if gh is not on PATH:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
python -m scripts.github_setup
```

GitHub CLI login is separate from the ChatGPT integration's authentication. The script checks authenticated identity, inspects anavo before creation, refuses nonpublic/mismatched repositories, refuses an unrelated origin, preserves history and stages only intended project paths. It refuses a nonempty remote with an unborn local branch and refuses divergent history. It never force-pushes or deletes locks. It publishes the current honest implementation status; it does not claim missing API/quantum validation has passed.

On success it verifies repository visibility/owner/name, main, local SHA, git ls-remote SHA, GitHub API SHA and expected remote files. The exact verified URL and hashes are saved to results/github_verification.json. No repository URL/hash is reported as successful until those checks actually run.

If a matching repository already has remote commits while this workspace remains unborn, stop and preserve both. Clone the verified repository to a new folder and compare/copy intended project changes there before committing; do not reset, force-push or overwrite the existing folder. This avoids creating unrelated histories or losing work. If the original session's `.git` writes remain restricted, use the ordinary terminal or reopen the project in a session that grants Git metadata writes.

## Full completion after GitHub

```powershell
.\scripts\finish_setup.ps1
```

This establishes/verifies GitHub first, installs dependencies, runs actual API/quantum checks and benchmarks, then commits/pushes the validated milestone. If any dependency or validation step fails it stops with the concrete error. Update report/pitch/tracker from the actual measured output before submission. GitHub connection is not proof of API or quantum correctness.
