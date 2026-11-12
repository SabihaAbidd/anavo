"""Run checks and write evidence; skips are explicit, never counted as passes."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest
from src.evaluation import environment_versions


def main():
    suite=unittest.defaultTestLoader.discover("tests")
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    record=dict(generated_utc=datetime.now(timezone.utc).isoformat(),
                command="python -m scripts.validate", tests_run=result.testsRun,
                passed=result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),
                skipped=[dict(test=str(test),reason=reason) for test,reason in result.skipped],
                failures=[dict(test=str(test),traceback=trace) for test,trace in result.failures],
                errors=[dict(test=str(test),traceback=trace) for test,trace in result.errors],
                environment=environment_versions(),
                complete_validation=not result.skipped and result.wasSuccessful(),
                complete_quantum_validation=result.wasSuccessful() and not any(
                    "QuantumTests" in str(test) or "RealQuantumAPI" in str(test) for test,_ in result.skipped),
                complete_api_validation=result.wasSuccessful() and not any(
                    "APITests" in str(test) for test,_ in result.skipped))
    path=Path("results/validation.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(f"Validation record: {record['passed']} passed; {len(result.skipped)} skipped; {len(result.failures)} failures; {len(result.errors)} errors")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
