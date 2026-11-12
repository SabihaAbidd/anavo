"""Run from repository root: python -m scripts.benchmark."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from src.scenarios import presets
from src.evaluation import compare


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="results/benchmark_results.json")
    parser.add_argument("--maxiter",type=int,default=80)
    parser.add_argument("--shots",type=int,default=2048)
    parser.add_argument("--require-quantum",action="store_true",help="Exit unsuccessfully unless every quantum run executes")
    args=parser.parse_args()
    results=[]
    for name in ("Ample backup","Limited battery","Mandatory infeasible"):
        result=compare(presets()[name],depth=2,shots=args.shots,maxiter=args.maxiter,seed=42)
        results.append(result)
        best=result["classical"]["best"]
        print(f"{name}: classical={best['utility'] if best else 'infeasible'}, quantum={result['quantum']['status']}")
    full=all(r["quantum"]["status"] != "unavailable" for r in results)
    document=dict(generated_utc=datetime.now(timezone.utc).isoformat(),
                  complete_quantum_execution=full,results=results)
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(document,indent=2,allow_nan=False),encoding="utf-8")
    print(f"Saved {path}; quantum complete={full}")
    if args.require_quantum and not full:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
