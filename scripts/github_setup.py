"""Authorized local CLI recovery: public owner/anavo, no duplicate/force/history replacement."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

DESCRIPTION = "Quantum-Assisted Energy Resilience Optimization for Pakistan"


def command(*args, check=True):
    result = subprocess.run(args, text=True, capture_output=True)
    if check and result.returncode:
        # Only ordinary gh/git output; never request or print credentials.
        raise RuntimeError(f"{' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result


def origin_matches(value, owner):
    expected = f"{owner}/anavo".casefold()
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?/?", value)
    return bool(match and match.group(1).casefold() == expected)


def main():
    root = Path(__file__).resolve().parent.parent
    import os
    os.chdir(root)
    if not shutil.which("gh"):
        raise RuntimeError("Install GitHub CLI: winget install --id GitHub.cli --exact ; then gh auth login --hostname github.com --git-protocol https --web")
    command("gh", "auth", "status", "--hostname", "github.com")
    profile = json.loads(command("gh", "api", "user").stdout)
    owner = profile["login"]
    full_name = f"{owner}/anavo"
    target_url = f"https://github.com/{full_name}.git"
    branch = command("git", "branch", "--show-current").stdout.strip()
    if branch != "main":
        raise RuntimeError(f"Current branch is {branch!r}; select the intended main branch without discarding work before continuing")
    existing_origin = command("git", "remote", "get-url", "origin", check=False)
    if existing_origin.returncode == 0 and not origin_matches(existing_origin.stdout.strip(), owner):
        raise RuntimeError("Existing origin points elsewhere; refusing to overwrite it")
    repo_result = command("gh", "api", f"repos/{full_name}", check=False)
    if repo_result.returncode:
        if "404" not in repo_result.stderr:
            raise RuntimeError("Repository lookup failed for a reason other than not found; no repository was created")
        command("gh", "repo", "create", full_name, "--public", "--description", DESCRIPTION)
        repo_result = command("gh", "api", f"repos/{full_name}")
    repo = json.loads(repo_result.stdout)
    if repo["private"] or repo["owner"]["login"].casefold() != owner.casefold() or repo["name"] != "anavo":
        raise RuntimeError("Repository ownership/name/public visibility does not match; refusing to change permissions or content")
    heads = command("git", "ls-remote", "--heads", target_url).stdout.strip()
    local_head = command("git", "rev-parse", "--verify", "HEAD", check=False)
    if heads:
        if local_head.returncode:
            raise RuntimeError("Remote is nonempty while this workspace has no commits. Refusing to overwrite or merge potentially unrelated history")
        remote_branch = repo.get("default_branch")
        if remote_branch != "main":
            raise RuntimeError("Existing repository default branch is not main; inspect its history before continuing")
        # Fetch objects only, preserve worktree and index; verify common ancestry before staging.
        command("git", "fetch", target_url, "main")
        ancestor = command("git", "merge-base", "--is-ancestor", "FETCH_HEAD", "HEAD", check=False)
        if ancestor.returncode:
            raise RuntimeError("Remote main is not an ancestor of local HEAD; no push/merge/force operation was performed")
    if existing_origin.returncode:
        command("git", "remote", "add", "origin", target_url)
    intended = [".gitignore", ".github", ".streamlit", "AGENTS.md", "PLAN.md", "TASKS.md", "README.md", "requirements.txt", "requirements-demo.txt", "requirements-lock.txt",
                "app.py", "legacy_demo", "backend", "frontend", "src", "tests", "scripts", "docs", "results"]
    command("git", "add", "--", *intended)
    staged = command("git", "diff", "--cached", "--quiet", check=False)
    if staged.returncode == 1:
        command("git", "commit", "-m", "feat: add backend-first Anavo API and validated optimization contracts")
    elif staged.returncode:
        raise RuntimeError("Could not inspect staging state")
    sha = command("git", "rev-parse", "HEAD").stdout.strip()
    command("git", "push", "-u", "origin", "main")
    remote_sha = command("git", "ls-remote", "origin", "refs/heads/main").stdout.split()[0]
    api_sha = json.loads(command("gh", "api", f"repos/{full_name}/commits/main").stdout)["sha"]
    if sha != remote_sha or sha != api_sha:
        raise RuntimeError("Push verification failed: local, Git remote and GitHub API SHAs differ")
    final_repo = json.loads(command("gh", "api", f"repos/{full_name}").stdout)
    if final_repo.get("default_branch") != "main" or final_repo["private"]:
        raise RuntimeError("Final branch/public visibility verification failed")
    for path in ("README.md", "PLAN.md", "TASKS.md", "backend/main.py", "src/quantum_solver.py"):
        command("gh", "api", f"repos/{full_name}/contents/{path}?ref=main")
    record = dict(repository_url=final_repo["html_url"], owner=owner, visibility="public",
                  branch="main", local_commit=sha, remote_commit=remote_sha,
                  api_commit=api_sha, files_verified=True, push_verified=True)
    # Keep verification outside the commit; a subsequent documentation commit can include it.
    Path("results/github_verification.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record,indent=2))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"GitHub setup blocked: {exc}",file=sys.stderr)
        sys.exit(1)
