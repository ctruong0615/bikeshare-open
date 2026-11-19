---
name: seed-fault
description: Demonstrate one named bikeshare verification failure, preserve real test and hook output, and restore the source. Use for controlled assignment fault demonstrations.
allowed-tools: Read, Edit, Bash(python *), Bash(make *), Bash(git diff *)
---

# Seed a fault: $ARGUMENTS

Accept `forbidden`, `rolling`, or `weather`. Invoke
`python scripts/seed_fault.py $ARGUMENTS` from the repository root.

The script requires the intended source fragment and no existing evidence
for that fault. It temporarily changes one fragment, captures the complete
pytest output and the PostToolUse hook's stderr, and restores the original
bytes in `finally`. It then reruns the tests on the restored source.

Read the resulting evidence under `docs/evidence/`. A demonstration counts
only if the broken test exits nonzero, the hook exits 2, and the repaired
tests pass. Summarize those exit codes, and append the exact mutation and
links to both logs to `docs/SEEDED_FAULTS.md`. Name the repair mechanism:
this scripted restoration is one deterministic repair action, not a claim
that a language model independently diagnosed the bug in one turn.

Do not overwrite existing evidence, change raw data, or try another mutation
if the chosen fragment is absent. Report that mismatch and inspect the diff.
