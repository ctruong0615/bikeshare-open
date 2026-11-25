# Team branch audits

The instructor's team clarification allows members to audit each other's
branches in one shared repository before merge. Each member must contribute
on a branch and audit a different member's branch in a fresh reviewer session.

| Reviewer | Branch author | Status |
|---|---|---|
| Calvin | Faline | Completed and verdict accepted on 2026-11-25; not yet merged |
| Faline | Andrew | Pending; no audit output received |
| Andrew | Calvin | Claude Code audit completed on 2026-11-25. It agrees with the approved provisional verdict. |

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

## Andrew audits Calvin — calendar-gap regression tests

- Branch [calvin/calendar-gap-tests](https://github.com/ctruong0615/bikeshare-open/tree/calvin/calendar-gap-tests).
- Reviewed commit `ae00fed0b819e0cf1e7aa1ac63722bf7f3d6a845`.
- Diff base `398fc667a92b976de2eed1b0f8a88a7db00474b9`, the merge base with the fetched `origin/main`.
- Independent checks performed on 2026-11-25 (Pacific time) in a detached worktree at the reviewed commit.

### Auditor output — verbatim

Claude Code 2.1.289 ran the repo's `leakage-auditor` in a fresh session
against the pinned diff. The model was `bikeshare-coder` built from
`qwen3.5:9b` via local Ollama 0.40.18 with a 65,536-token context.
`make check-model` observed a successful tool call despite a warning about
advertised tool support. [Successful preflight](evidence/peer-calvin-ae00fed/check-model-success.txt),
[initial preflight failure](evidence/peer-calvin-ae00fed/check-model.txt).

The first pass gathered the exact diff and read the relevant code and tests.
It stalled before producing a report and recorded a Claude Code stream error.
The same reviewer session was resumed with tools disabled to produce the
report below. Claude Code denied the reviewer's direct pytest invocation.
The passing test counts come from the independent runs.
[Run metadata](evidence/peer-calvin-ae00fed/audit-metadata.json),
[Claude Code result](evidence/peer-calvin-ae00fed/claude-result.json),
[verbatim text](evidence/peer-calvin-ae00fed/auditor-verbatim.txt).

````text
## Leakage Auditor Report

Commit `ae00fed0b819e0cf1e7aa1ac63722bf7f3d6a845` against base `398fc667a92b976de2eed1b0f8a88a7db00474b9`.

### Finding
**Only adds a test file.** This commit introduces `tests/test_calendar_gap.py` with four regression tests validating the existing calendar-gap handling in `src/features.py`. **No implementation code was modified** between these commits.

### Verification of Five Checks (via reading current state)
1. **Target leakage:** PASS — lag features use `.shift(1)` before aggregation; `feature_columns()` filters out `FORBIDDEN` which includes `"cnt"`, `"casual"`, `"registered"` (config lines 24, 32, 47).
2. **Temporal ordering:** PASS — all lags shift before rolling aggregations (features.py lines 74-76); `temporal_split()` in train.py splits by date (lines 57-63); models fit only on train data.
3. **Calendar gaps:** PASS — `reindex_to_calendar()` inserts missing days (features.py line 44); test validates excluded range and independence from today's count.
4. **Silent row loss:** PASS — `dropna()` at line 79 is bounded by `test_contract.py`'s `test_only_expected_rows_are_dropped()` asserting lost rows ≤ LAG_WARMUP × (1 + missing_days).
5. **Unreported baseline:** PASS — `baseline_mean` (line 50) and `baseline_persistence` (line 51, predicts `cnt_lag_1`) both appear alongside ridge and hgb.

All five checks pass. The commit safely adds validation tests without altering any numbers or conclusions.
````

### Independent checks

```text
git diff 398fc667a92b976de2eed1b0f8a88a7db00474b9...HEAD
python3 -B -m pytest tests/test_calendar_gap.py -vv -p no:cacheprovider
python3 -B -m pytest tests/ -q -p no:cacheprovider
```

All four targeted cases and all 23 suite tests passed. The runs used the
installed Python 3.12.1, NumPy 1.26.4, pandas 2.2.3, scikit-learn 1.7.2 and
pytest 8.1.1. These package versions differ from the repository pins. The
base and reviewed commit have identical `src/` trees and identical
`reports/metrics.json` blobs. [Targeted tests](evidence/peer-calvin-ae00fed/target-tests.txt),
[full suite](evidence/peer-calvin-ae00fed/full-tests.txt).

### Andrew's approved provisional verdict

Andrew approved this provisional verdict in chat on 2026-11-25. It covers
the independent checks performed at the reviewed commit.

My independent review found no result-changing issue in Calvin's commit.
The four new cases check exclusion of dates with incomplete history after
the March 10 gap and sample variability from the previous seven calendar
days on each side of the gap. They also confirm that changing today's count
leaves today's variability unchanged and affects tomorrow's variability.
All four targeted cases and all 23 branch tests passed. The diff adds
regression coverage and leaves the forecast pipeline and reported metrics
unchanged.

The completed auditor report agrees with Andrew's approved provisional
verdict. It found no result-changing issue in this test-only diff.

### Team SDK self-audit

[`reports/audit.jsonl`](../reports/audit.jsonl) already contains the
successful SDK result recorded in `b2084dfb178bdb44e880cc6fab17ded89d2fc905`.
It reports no leakage, valid temporal ordering, both baselines and
reproducibility. `REPORT.md` records the verification limits of that run.
A run on the final integrated commit is still pending, along with the
final integrated tests and the outstanding peer reviews.
