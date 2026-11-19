"""Show that Bash cp bypasses the edit hook, while the raw hash guard catches it."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/bike_daily.csv"
EVIDENCE = ROOT / "docs/evidence"


if __name__ == "__main__":
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record = EVIDENCE / "raw-copy.json"
    if record.exists():
        raise SystemExit("Raw-copy evidence already exists; refusing to overwrite")
    original = RAW.read_bytes()
    original_hash = hashlib.sha256(original).hexdigest()
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    bash = shutil.which("bash")
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        probe = Path(directory) / "fault.csv"
        probe.write_bytes(original + b"\n")
        try:
            copied = subprocess.run([bash, "-c", 'cp "$1" data/raw/bike_daily.csv',
                                     "fault-probe", probe.as_posix()], cwd=ROOT,
                                    capture_output=True, text=True)
            hook = subprocess.run([bash, ".claude/hooks/check_leakage.sh"], cwd=ROOT,
                                  input=json.dumps({"tool_name": "Bash", "tool_input": {
                                      "command": "cp fault.csv data/raw/bike_daily.csv"}}),
                                  env=env, capture_output=True, text=True)
            guard = subprocess.run([sys.executable, "-m", "src.ingest"], cwd=ROOT,
                                   capture_output=True, text=True)
            stop = subprocess.run([sys.executable, ".claude/hooks/verify_stop.py"], cwd=ROOT,
                                  input='{"stop_hook_active": false}', env=env,
                                  capture_output=True, text=True)
            (EVIDENCE / "raw-copy.guard.txt").write_text(guard.stdout + guard.stderr)
            (EVIDENCE / "raw-copy.hook.stderr.txt").write_text(hook.stderr)
            (EVIDENCE / "raw-copy.stop.stderr.txt").write_text(stop.stderr)
        finally:
            RAW.write_bytes(original)
    result = {
        "command": 'cp "$1" data/raw/bike_daily.csv',
        "mutation": "append one newline to an otherwise identical CSV",
        "cp_exit": copied.returncode, "posttool_hook_exit": hook.returncode,
        "posttool_hook_stderr": hook.stderr,
        "ingest_hash_guard_exit": guard.returncode, "stop_hook_exit": stop.returncode,
        "original_sha256": original_hash,
        "restored_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
    }
    record.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    assert copied.returncode == 0 and hook.returncode == 0
    assert guard.returncode != 0 and stop.returncode == 2
    assert result["restored_sha256"] == original_hash
