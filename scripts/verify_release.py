"""Strict submission gate: green skipped tests do not imply a working quantum demo."""
import json
from pathlib import Path
import subprocess
import sys
import unittest


def main():
    suite=unittest.defaultTestLoader.discover("tests")
    outcome=unittest.TextTestRunner(verbosity=2).run(suite)
    problems=[]
    if not outcome.wasSuccessful() or outcome.skipped:
        problems.append("All tests must pass with zero skips, including real Qiskit/Aer tests")
    startup=Path("results/api_startup_check.json")
    if not startup.exists() or not json.loads(startup.read_text(encoding="utf-8")).get("healthy"):
        problems.append("A successful FastAPI localhost startup check is required: python -m scripts.api_startup_check")
    path=Path("results/benchmark_results.json")
    if not path.exists():
        problems.append("Run python -m scripts.benchmark --require-quantum")
    else:
        data=json.loads(path.read_text(encoding="utf-8"))
        if not data.get("complete_quantum_execution"):
            problems.append("Benchmark quantum execution is incomplete")
        results=data.get("results",[])
        if len(results)<3:
            problems.append("Three benchmark scenarios are required")
        for r in results:
            q=r.get("quantum",{})
            if not q.get("counts") or sum(q["counts"].values()) != q.get("shots"):
                problems.append(f"Missing/invalid measured shots for {r['scenario']['name']}")
        if not any(r.get("objective_gap") is not None for r in results):
            problems.append("No measured feasible quantum/classical comparison exists")
    try:
        subprocess.run(["git","rev-parse","--verify","HEAD"],check=True,capture_output=True)
    except (subprocess.CalledProcessError,FileNotFoundError):
        problems.append("No Git commit exists")
    if problems:
        print("RELEASE BLOCKED:")
        for problem in problems:
            print(" - "+problem)
        return 1
    print("Local scientific checks passed. Verify remote push and submission checklist separately.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
