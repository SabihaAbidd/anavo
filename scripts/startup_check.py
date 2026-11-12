"""Launch Streamlit temporarily and record its real localhost health response."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request


def main():
    Path("results").mkdir(exist_ok=True)
    record=dict(checked_utc=datetime.now(timezone.utc).isoformat(),healthy=False,
                command="python -m scripts.startup_check")
    with Path("results/startup.log").open("w",encoding="utf-8") as log:
        process=subprocess.Popen([sys.executable,"-m","streamlit","run","app.py",
            "--server.headless=true","--server.address=127.0.0.1","--server.port=8517",
            "--browser.gatherUsageStats=false"],stdout=log,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+45
            while time.monotonic()<deadline:
                if process.poll() is not None:
                    record["process_exit_code"]=process.returncode
                    break
                try:
                    with urllib.request.urlopen("http://127.0.0.1:8517/_stcore/health",timeout=1) as response:
                        record.update(healthy=response.status==200,status_code=response.status,
                                      body=response.read().decode())
                        record.pop("last_error",None)
                        break
                except OSError as exc:
                    record["last_error"]=str(exc)
                    time.sleep(.5)
        finally:
            process.terminate()
            process.wait(timeout=10)
    Path("results/startup_check.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record))
    return 0 if record["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
