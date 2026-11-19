"""Final deterministic check, including raw integrity, even after Bash edits."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    payload = json.load(sys.stdin)
    if payload.get("stop_hook_active"):
        raise SystemExit(0)
    for args in ([sys.executable, "-m", "src.ingest"],
                 [sys.executable, "-m", "pytest", "tests/", "-q"]):
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            print("Final verification failed; repair before claiming completion.", file=sys.stderr)
            print(result.stdout + result.stderr, file=sys.stderr)
            raise SystemExit(2)
