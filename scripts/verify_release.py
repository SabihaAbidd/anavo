"""Strict submission gate: green skipped tests do not imply a working quantum demo."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from .validate import run_validation
from .provenance import source_fingerprint
from .evidence import load_record,check_http_evidence,check_benchmark_evidence


def main():
    record,outcome=run_validation()
    problems=[]
    if not outcome.wasSuccessful() or outcome.skipped or outcome.testsRun==0:
        problems.append("All tests must pass with zero skips, including real Qiskit/Aer tests")
    fingerprint=source_fingerprint()
    for path,check in (("results/api_startup_check.json",check_http_evidence),
                       ("results/benchmark_results.json",check_benchmark_evidence)):
        data,error=load_record(path)
        if error: problems.append(error)
        else: problems.extend(check(data,fingerprint))
    try:
        subprocess.run(["git","rev-parse","--verify","HEAD"],check=True,capture_output=True)
    except (subprocess.CalledProcessError,FileNotFoundError):
        problems.append("No Git commit exists")
    Path("results/release_check.json").write_text(json.dumps(dict(
        checked_utc=datetime.now(timezone.utc).isoformat(),source_fingerprint=fingerprint,
        ready=not problems,exit_code=1 if problems else 0,reasons=problems),indent=2),encoding="utf-8")
    if problems:
        print("RELEASE BLOCKED:")
        for problem in problems:
            print(" - "+problem)
        return 1
    print("Local scientific checks passed. Verify remote push and submission checklist separately.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
