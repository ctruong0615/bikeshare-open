---
name: seed-fault
description: Demonstrate one named bikeshare verification failure, preserve real test and hook output, and restore the source. Use for controlled assignment fault demonstrations.
allowed-tools: Read, Edit, Bash(python *), Bash(make *), Bash(git diff *)
---

# Seed a fault: $ARGUMENTS

Accept `forbidden`, `rolling`, or `weather`. Invoke
`python scripts/seed_fault.py $ARGUMENTS` from the repository root.

The script requires the intended source fragment and chooses the next unused
attempt prefix, preserving prior evidence. It temporarily changes one fragment, captures the complete
pytest output and the PostToolUse hook's stderr, and restores the original
bytes in `finally`. It then reruns the tests on the restored source.

The script appends the exact mutation and real logs to `docs/SEEDED_FAULTS.md`.
A demonstration counts
only if the broken test exits nonzero, the hook exits 2, and the repaired
tests pass. Summarize the printed exit codes and the returned `evidence_prefix` without
editing or searching other files. Name the repair mechanism:
this scripted restoration is one deterministic repair action, not a claim
that a language model independently diagnosed the bug in one turn.

Do not overwrite existing evidence, change raw data, or try another mutation
if the chosen fragment is absent. Report that mismatch and inspect the diff.
