"""Probe a real Uvicorn health endpoint; in-process tests do not replace this."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import socket
import urllib.error
import urllib.request
from .provenance import source_fingerprint
from .http_checks import run_http_checks


def main():
    Path("results").mkdir(exist_ok=True)
    record=dict(checked_utc=datetime.now(timezone.utc).isoformat(),healthy=False,
                source_fingerprint=source_fingerprint(),checks=[],
                command="python -m scripts.api_startup_check")
    missing=[name for name in ("fastapi","uvicorn") if not importlib.util.find_spec(name)]
    if missing:
        record["reason"]="Missing runtime dependencies: "+", ".join(missing)
    else:
        try:
            with socket.socket() as reservation:
                reservation.bind(("127.0.0.1",0))
                port=reservation.getsockname()[1]
            record["endpoint"]=f"http://127.0.0.1:{port}/health"
            with Path("results/api_startup.log").open("w",encoding="utf-8") as log:
                process=subprocess.Popen([sys.executable,"-m","uvicorn","backend.main:app",
                    "--host","127.0.0.1","--port",str(port),"--no-access-log"],stdout=log,stderr=subprocess.STDOUT)
                try:
                    deadline=time.monotonic()+40
                    while time.monotonic()<deadline:
                        if process.poll() is not None:
                            record["process_exit_code"]=process.returncode
                            break
                        try:
                            with urllib.request.urlopen(record["endpoint"],timeout=1) as response:
                                body=json.load(response)
                                if body.get("service")=="ANAVO API" and body.get("status")=="ok":
                                    record["checks"]=run_http_checks(f"http://127.0.0.1:{port}")
                                    record["healthy"]=all(c["passed"] for c in record["checks"])
                                    break
                        except (OSError,ValueError) as exc:
                            record["last_error"]=str(exc)
                            time.sleep(.5)
                finally:
                    process.terminate()
                    process.wait(timeout=10)
        except (OSError,subprocess.SubprocessError) as exc:
            record["reason"]=str(exc)
    Path("results/api_startup_check.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps({key:value for key,value in record.items() if key!="checks"}))
    for check in record["checks"]: print(f"{check['name']}: {'PASS' if check['passed'] else 'FAIL'}")
    return 0 if record["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
