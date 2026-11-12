"""Probe a real Uvicorn health endpoint; in-process tests do not replace this."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request


def main():
    Path("results").mkdir(exist_ok=True)
    record=dict(checked_utc=datetime.now(timezone.utc).isoformat(),healthy=False,
                command="python -m scripts.api_startup_check",endpoint="http://127.0.0.1:8017/health")
    if not importlib.util.find_spec("fastapi"):
        record["reason"]="FastAPI is not installed; HTTP startup cannot execute"
    else:
        with Path("results/api_startup.log").open("w",encoding="utf-8") as log:
            process=subprocess.Popen([sys.executable,"-m","uvicorn","backend.main:app",
                "--host","127.0.0.1","--port","8017"],stdout=log,stderr=subprocess.STDOUT)
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
                                record.update(healthy=True,status_code=response.status,response=body)
                                break
                    except (OSError,ValueError) as exc:
                        record["last_error"]=str(exc)
                        time.sleep(.5)
            finally:
                process.terminate()
                process.wait(timeout=10)
    Path("results/api_startup_check.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record))
    return 0 if record["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
