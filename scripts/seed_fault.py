"""Repeatable, reversible fault demonstration; all evidence is real output."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/features.py"
EVIDENCE = ROOT / "docs/evidence"
FAULTS = {
    "forbidden": (
        'return [c for c in numeric if c not in FORBIDDEN]',
        'return [c for c in numeric if c not in FORBIDDEN] + ["casual"]',
    ),
    "rolling": (
        'out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()',
        'out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()',
    ),
    "weather": (
        'raise ValueError(f"unmapped weather labels: {sorted(unknown)}")',
        'pass  # seeded fault: silently map unexpected labels to NaN',
    ),
}


def command(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kwargs)


def run(name, attempt=None):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if attempt is None:
        attempt = 1
        while (EVIDENCE / (name if attempt == 1 else f"{name}-attempt-{attempt}")).with_suffix(".json").exists():
            attempt += 1
    prefix = EVIDENCE / (name if attempt == 1 else f"{name}-attempt-{attempt}")
    if prefix.with_suffix(".json").exists():
        raise SystemExit(f"Evidence already exists for {name}; refusing to overwrite")
    old, new = FAULTS[name]
    original = SOURCE.read_bytes()
    if original.count(old.encode()) != 1:
        raise SystemExit("Expected source fragment is absent or ambiguous")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    try:
        SOURCE.write_bytes(original.replace(old.encode(), new.encode()))
        red = command([sys.executable, "-m", "pytest", "tests/", "-q"])
        hook = command([shutil.which("bash"), ".claude/hooks/check_leakage.sh"],
                       input=json.dumps({"tool_name": "Edit", "tool_input": {
                           "file_path": SOURCE.as_posix()}}), env=env)
        prefix.with_suffix(".pytest.txt").write_text(red.stdout + red.stderr, encoding="utf-8")
        prefix.with_suffix(".hook.stderr.txt").write_text(hook.stderr, encoding="utf-8")
        prefix.with_suffix(".hook.stdout.txt").write_text(hook.stdout, encoding="utf-8")
    finally:
        SOURCE.write_bytes(original)
    green = command([sys.executable, "-m", "pytest", "tests/", "-q"])
    prefix.with_suffix(".repaired.txt").write_text(green.stdout + green.stderr, encoding="utf-8")
    result = {"fault": name, "attempt": attempt,
              "evidence_prefix": prefix.relative_to(ROOT).as_posix(), "old": old, "new": new,
              "pytest_exit": red.returncode, "hook_exit": hook.returncode,
              "repair": "restore original bytes in finally", "repair_actions": 1,
              "repaired_pytest_exit": green.returncode,
              "agent": "Codex orchestrated; no local-model repair turn"}
    prefix.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if red.returncode == 0 or hook.returncode != 2 or green.returncode != 0:
        raise SystemExit("Fault demonstration did not meet its verification contract")
    notes = ROOT / "docs/SEEDED_FAULTS.md"
    with notes.open("a", encoding="utf-8", newline="\n") as output:
        output.write(f"\n## Repeated {name} demonstration, attempt {attempt}\n\n")
        output.write("One deterministic byte-restoration action; no independent model debugging turn.\n\n")
        output.write(f"```diff\n-{old}\n+{new}\n```\n\n")
        output.write(f"pytest exit {red.returncode}; hook exit {hook.returncode}; repaired pytest exit {green.returncode}.\n\n")
        output.write("Actual red test output:\n```text\n" + red.stdout + red.stderr + "\n```\n\n")
        output.write("Actual hook stderr:\n```text\n" + hook.stderr + "\n```\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fault", choices=list(FAULTS))
    parser.add_argument("--attempt", type=int)
    args = parser.parse_args()
    run(args.fault, args.attempt)
