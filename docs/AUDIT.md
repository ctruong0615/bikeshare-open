# Team branch audits

The instructor's team clarification allows members to audit each other's
branches in one shared repository before merge. Each member must contribute
on a branch and audit a different member's branch in a fresh reviewer session.

| Reviewer | Branch author | Status |
|---|---|---|
| Calvin | Faline | Completed and verdict accepted on 2026-11-25; not yet merged |
| Faline | Andrew | Pending; no audit output received |
| Andrew | Calvin | Pending; no audit output received |

## Calvin audits Faline — target reconstruction

- Branch: `teammate-b/target-reconstruction`.
- Audited commit: `029f21ebd779ba1121888d1bf120bac7ce24f93b`.
- Base: `398fc667a92b976de2eed1b0f8a88a7db00474b9`.
- Date: 2026-11-25, America/Los_Angeles.
- Reviewer: Calvin; Codex operated a fresh Claude Code `leakage-auditor`
  session using local `bikeshare-coder` (`qwen3.5:9b`, 65,536-token context).
- The review session did not contain Faline's authoring conversation.
- Scope: `src/experiment.py` and `tests/test_target_transformation.py`.

### Auditor output — verbatim

````text
## Audit Report for Commit 029f21ebd779ba1121888d1bf120bac7ce24f93b

**Files reviewed:** `src/experiment.py`, `tests/test_target_transformation.py` against baseline.

### Check Results

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | **Target leakage** | ✓ Pass | Lag features use `.shift(1)` after calendar reindex; `cnt_lag_1` for date d contains cnt from d-1 (verified in `test_lags_are_true_calendar_lags`). No arithmetic combinations of target appear in feature set (`FORBIDDEN` excludes `casual`, `registered`, `cnt`). |
| 2 | **Temporal ordering** | ✓ Pass | Models fit on train (2011), predict on valid/test (2012). `temporal_split` uses date thresholds, not random. No transformers fit on validation/test rows. Experiment reconstruction uses yesterday's observed count as anchor, never today's target. |
| 3 | **Calendar gaps** | ✓ Pass | `reindex_to_calendar` fills missing days (e.g., 2011-03-10) before shifting; `.shift(1)` then operates on gap-free calendar index. Test `test_calendar_is_complete_before_lagging` verifies this. |
| 4 | **Silent row loss** | ✓ Pass | Weather encoding fails loudly on unknown labels (test `test_unknown_weather_fails_loudly`). `dropna()` only removes warmup-period rows, bounded by `LAG_WARMUP`. Test `test_only_expected_rows_are_dropped` asserts row loss is within allowed bounds. |
| 5 | **Unreported baseline** | ✓ Pass | `baseline_persistence` in `MODELS` predicts yesterday's count; `baseline_mean` also present. Both reported in metrics alongside trained models (see `src/train.py`). |

### Test Suite Status
All 20 tests pass after applying the diff:
```
tests/test_contract.py::... PASSED
tests/test_leakage.py::... PASSED  
tests/test_split.py::... PASSED
tests/test_target_transformation.py::test_reconstruct_counts_adds_predicted_deltas PASSED
```

### New Function in `src/experiment.py`
The `reconstruct_counts` function is a simple helper that adds predicted delta to yesterday's count. The test verifies correct arithmetic behavior only—it does not verify correctness relative to ground truth counts, which would require integration testing against the training pipeline (not covered by unit tests).

### Findings Summary
No substantive findings. All five checks pass. The diff introduces:
1. A new helper function in `src/experiment.py` that correctly reconstructs transformed targets
2. A corresponding unit test that verifies the arithmetic operation

Neither change invalidates any conclusion or alters model behavior negatively.
````

### Checks run and evidence

```text
git diff origin/main...HEAD
python -m pytest tests/test_target_transformation.py -q -p no:cacheprovider
python -m pytest tests/ -q -p no:cacheprovider
```

The targeted test passed (1 passed) and the full suite on Faline's branch
passed (20 passed). See the [targeted log](evidence/peer-faline-029f21e/target-tests.txt) and
[full-suite log](evidence/peer-faline-029f21e/full-tests.txt). Codex independently executed the
original and refactored validation experiment in the same environment:
both returned R2 0.5642 and MAE 885.8, with 348 training rows and 182
validation rows. The exact result dictionaries are in
[independent-checks.json](evidence/peer-faline-029f21e/independent-checks.json). The comparison
did not score the test period; the inherited full suite includes its fixed
holdout smoke assertion.

The reviewer reached turn limits during two evidence-gathering runs. The
same isolated reviewer session then produced the final report with further
tools disabled. Raw records are preserved as
[initial run](evidence/peer-faline-029f21e/claude-run.json),
[continued run](evidence/peer-faline-029f21e/claude-run-continued.json), and
[final report](evidence/peer-faline-029f21e/claude-final.json). The [plain-text output](evidence/peer-faline-029f21e/auditor-verbatim.txt)
is also retained without editing. No source files were changed by this audit.

### Calvin's accepted verdict

The following verdict was drafted with Codex assistance and explicitly
accepted by Calvin in chat on 2026-11-25:

I agree that Faline's two-file change introduces no substantive methodology
issue: it extracts the same NumPy addition into a helper, without changing
training targets, time splits, model inputs or prediction reconstruction.
The new test covers positive, negative and zero deltas. The targeted test
and all 20 branch tests passed, and the original and refactored validation
results matched exactly. I agree with the auditor's unit-test limitation:
the new test alone is arithmetic coverage rather than an end-to-end model
test; the independent validation comparison supplies additional evidence.
One detail in the auditor's row-loss description is imprecise: the 14 lost
raw rows include seven warm-up days plus seven days affected by the missing
calendar observation, not only warm-up. That inherited behavior is covered
by the existing tests and is not a regression from this branch.

Status: audit accepted for the exact commit above; branch remains unmerged.
If the branch changes, review the new diff before merging it.
