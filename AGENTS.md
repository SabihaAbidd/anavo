# ANAVO project instructions

## Authorized development workflow

The user authorizes automatic Git commits and pushes after each meaningful, validated development milestone. Do not ask again for routine commit/push approval. This authorization applies only to this project and its existing repository, https://github.com/SabihaAbidd/anavo, on main.

1. Preserve existing work/history and inspect the working tree before editing.
2. Implement the requested change and run checks appropriate to that change. Accurately record failing checks, dependency skips, and unresolved blockers; do not describe unexecuted API/quantum tests as passed.
3. Update TASKS.md and relevant documentation with actual evidence.
4. Review and stage only intended project files. Exclude credentials, environments, caches and temporary data. Never absorb unrelated staged changes.
5. Create a descriptive milestone commit, push to the verified origin/main, and verify the remote SHA. Report the actual verified commit.
6. If local Git metadata/network permissions prevent publishing, report the concrete blocker immediately. An authorized GitHub contents/commit API is an alternative only when it actually has write permission; distinguish API publication from local checkout synchronization.
7. Never bypass execution restrictions, force-push, delete locks, rewrite history, expose credentials or change account permissions to make a commit succeed. A successful user-run terminal push does not change the agent session's permissions. Do not claim automatic publishing is operational until a real agent-initiated commit/push succeeds.

## Project scope

Final architecture: React + TypeScript + Vite -> Python/FastAPI/Pydantic -> Qiskit/Aer or the classical solver, with NumPy and SciPy. Reuse the validated optimization engine. Streamlit is optional legacy code only: preserve app.py and historical checks, keep its dependency in requirements-demo.txt, and exclude legacy_demo/tests from backend CI/release. The user supplied the design reference and authorized React implementation on 2026-11-12. Keep frontend/ separate from backend/ and the optimization engine. Keep mandatory constraints explicit and never fabricate quantum measurements or claim quantum speedup.
