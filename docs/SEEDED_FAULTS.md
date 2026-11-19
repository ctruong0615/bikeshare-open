# Seeded faults and verification evidence

All output below was captured from actual runs on 2026-11-18. Codex orchestrated these demonstrations. Each repair restored the saved source bytes in one deterministic repair action; these are not invented local-model troubleshooting conversations. The script was reused for all three source faults through the workflow packaged in `.claude/skills/seed-fault/SKILL.md`.

## New feature: failing test committed first

The local qwen3.5:9b `/new-feature` attempt replaced existing tests and invented counts. It was interrupted, its patch saved in `docs/evidence/local-model-rejected-test.patch`, and the tests restored. Codex then wrote the corrected named-date test using counts actually read from the CSV: 1349, 1562, 1600, 1606, 1510, 959, 822 for Jan 3–9, 2011. The corrected test was committed in 68acc02 before implementation in 1f6d9e0.

```text
python -m pytest tests/ -q
.............F....                                                       [100%]
================================== FAILURES ===================================
______________________ test_cnt_roll_std_7_on_2011_01_10 ______________________

self = Index(['instant', 'season', 'yr', 'mnth', 'holiday', 'weekday', 'temp',
       'atemp', 'hum', 'windspeed', 'casual', ...kday', 'month_sin', 'month_cos',
       'weather_severity', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7'],
      dtype='str')
key = 'cnt_roll_std_7'

    def get_loc(self, key):
        """
        Get integer location, slice or boolean mask for requested label.
    
        Parameters
        ----------
        key : label
            The key to check its location if it is present in the index.
    
        Returns
        -------
        int if unique index, slice if monotonic index, else mask
            Integer location, slice or boolean mask.
    
        See Also
        --------
        Index.get_slice_bound : Calculate slice bound that corresponds to
            given label.
        Index.get_indexer : Computes indexer and mask for new index given
            the current index.
        Index.get_non_unique : Returns indexer and masks for new index given
            the current index.
        Index.get_indexer_for : Returns an indexer even when non-unique.
    
        Examples
        --------
        >>> unique_index = pd.Index(list("abc"))
        >>> unique_index.get_loc("b")
        1
    
        >>> monotonic_index = pd.Index(list("abbc"))
        >>> monotonic_index.get_loc("b")
        slice(1, 3, None)
    
        >>> non_monotonic_index = pd.Index(list("abcb"))
        >>> non_monotonic_index.get_loc("b")
        array([False,  True, False,  True])
        """
        casted_key = self._maybe_cast_indexer(key)
        try:
>           return self._engine.get_loc(casted_key)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.venv\Lib\site-packages\pandas\core\indexes\base.py:3641: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
pandas/_libs/index.pyx:168: in pandas._libs.index.IndexEngine.get_loc
    ???
pandas/_libs/index.pyx:197: in pandas._libs.index.IndexEngine.get_loc
    ???
pandas/_libs/hashtable_class_helper.pxi:7668: in pandas._libs.hashtable.PyObjectHashTable.get_item
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

>   ???
E   KeyError: 'cnt_roll_std_7'

pandas/_libs/hashtable_class_helper.pxi:7676: KeyError

The above exception was the direct cause of the following exception:

feats =         dteday  instant  season  ...  cnt_lag_1 cnt_lag_7   cnt_roll_7
0   2011-01-10     10.0  WINTER  ...      822.0...    1787.0  1530.142857
713 2012-12-31    731.0  WINTER  ...     1796.0     920.0  1531.428571

[714 rows x 28 columns]

    def test_cnt_roll_std_7_on_2011_01_10(feats):
        """Sample std from Jan 3--9; Jan 10's count must not enter the window."""
        counts = [1349, 1562, 1600, 1606, 1510, 959, 822]
        raw = load_raw().set_index("dteday")
        dates = pd.date_range("2011-01-03", "2011-01-09", freq="D")
        assert raw.loc[dates, TARGET].tolist() == counts
        mean = sum(counts) / 7
        expected = (sum((value - mean) ** 2 for value in counts) / 6) ** 0.5
>       assert feats.set_index("dteday").loc[
            pd.Timestamp("2011-01-10"), "cnt_roll_std_7"
        ] == pytest.approx(expected)

tests\test_leakage.py:85: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv\Lib\site-packages\pandas\core\indexing.py:1199: in __getitem__
    return self.obj._get_value(*key, takeable=self._takeable)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\pandas\core\frame.py:4489: in _get_value
    series = self._get_item(col)
             ^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\pandas\core\frame.py:4969: in _get_item
    loc = self.columns.get_loc(item)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = Index(['instant', 'season', 'yr', 'mnth', 'holiday', 'weekday', 'temp',
       'atemp', 'hum', 'windspeed', 'casual', ...kday', 'month_sin', 'month_cos',
       'weather_severity', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7'],
      dtype='str')
key = 'cnt_roll_std_7'

    def get_loc(self, key):
        """
        Get integer location, slice or boolean mask for requested label.
    
        Parameters
        ----------
        key : label
            The key to check its location if it is present in the index.
    
        Returns
        -------
        int if unique index, slice if monotonic index, else mask
            Integer location, slice or boolean mask.
    
        See Also
        --------
        Index.get_slice_bound : Calculate slice bound that corresponds to
            given label.
        Index.get_indexer : Computes indexer and mask for new index given
            the current index.
        Index.get_non_unique : Returns indexer and masks for new index given
            the current index.
        Index.get_indexer_for : Returns an indexer even when non-unique.
    
        Examples
        --------
        >>> unique_index = pd.Index(list("abc"))
        >>> unique_index.get_loc("b")
        1
    
        >>> monotonic_index = pd.Index(list("abbc"))
        >>> monotonic_index.get_loc("b")
        slice(1, 3, None)
    
        >>> non_monotonic_index = pd.Index(list("abcb"))
        >>> non_monotonic_index.get_loc("b")
        array([False,  True, False,  True])
        """
        casted_key = self._maybe_cast_indexer(key)
        try:
            return self._engine.get_loc(casted_key)
        except KeyError as err:
            if isinstance(casted_key, slice) or (
                isinstance(casted_key, abc.Iterable)
                and any(isinstance(x, slice) for x in casted_key)
            ):
                raise InvalidIndexError(key) from err
>           raise KeyError(key) from err
E           KeyError: 'cnt_roll_std_7'

.venv\Lib\site-packages\pandas\core\indexes\base.py:3648: KeyError
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_cnt_roll_std_7_on_2011_01_10 - KeyError: '...
1 failed, 17 passed in 4.23s
make: *** [Makefile:16: test] Error 1

```

## Forbidden column

Exact change:

```diff
-return [c for c in numeric if c not in FORBIDDEN]
+return [c for c in numeric if c not in FORBIDDEN] + ["casual"]
```

Repair: restore original bytes in finally. One Codex orchestration turn / one scripted restore action; no local-model repair turn. Broken pytest exit 1; hook exit 2; repaired pytest exit 0.

Actual red test output:
```text
......F..........                                                        [100%]
================================== FAILURES ===================================
_________________________ test_no_forbidden_features __________________________

feats =         dteday  instant  season  ...  cnt_lag_1 cnt_lag_7   cnt_roll_7
0   2011-01-10     10.0  WINTER  ...      822.0...    1787.0  1530.142857
713 2012-12-31    731.0  WINTER  ...     1796.0     920.0  1531.428571

[714 rows x 28 columns]

    def test_no_forbidden_features(feats):
        """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
        construction, so this cannot discover a *new* leaky column. What it
        catches is someone editing feature_columns() or FORBIDDEN -- which is
        exactly the fault the Step 7 hook demonstrates."""
        cols = set(feature_columns(feats))
>       assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7', 'dayofweek', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})

tests\test_leakage.py:34: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 16 passed in 3.89s

```

Actual hook stderr:
```text
Leakage tests failed after editing C:/Users/Calvin/Documents/Codex/2026-11-18/https-dsc-capstone-org-2026-27/outputs/bikeshare-open/src/features.py:
feats =         dteday  instant  season  ...  cnt_lag_1 cnt_lag_7   cnt_roll_7
0   2011-01-10     10.0  WINTER  ...      822.0...    1787.0  1530.142857
713 2012-12-31    731.0  WINTER  ...     1796.0     920.0  1531.428571

[714 rows x 28 columns]

    def test_no_forbidden_features(feats):
        """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
        construction, so this cannot discover a *new* leaky column. What it
        catches is someone editing feature_columns() or FORBIDDEN -- which is
        exactly the fault the Step 7 hook demonstrates."""
        cols = set(feature_columns(feats))
>       assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7', 'dayofweek', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})

tests\test_leakage.py:34: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 8 passed in 1.56s

```

Actual repaired test output:
```text
.................                                                        [100%]
17 passed in 3.38s

```

## Unshifted rolling mean

Exact change:

```diff
-out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
+out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()
```

Repair: restore original bytes in finally. One Codex orchestration turn / one scripted restore action; no local-model repair turn. Broken pytest exit 1; hook exit 2; repaired pytest exit 0.

Actual red test output:
```text
.........F.......                                                        [100%]
================================== FAILURES ===================================
______________________ test_rolling_mean_excludes_today _______________________

feats =         dteday  instant  season  ...  cnt_lag_1 cnt_lag_7   cnt_roll_7
0   2011-01-10     10.0  WINTER  ...      822.0...    1787.0  1531.428571
713 2012-12-31    731.0  WINTER  ...     1796.0     920.0  1789.857143

[714 rows x 28 columns]

    def test_rolling_mean_excludes_today(feats):
        """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
        by_date = feats.set_index("dteday")[TARGET]
        date = feats.dteday.iloc[200]
        window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
        if all(d in by_date.index for d in window):
            expected = sum(by_date[d] for d in window) / 7
>           assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E           assert np.float64(4389.0) == 4414.857142857143 ï¿½ 0.00441486
E             
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ï¿½ 0.00441486

tests\test_leakage.py:60: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 16 passed in 3.86s

```

Actual hook stderr:
```text
Leakage tests failed after editing C:/Users/Calvin/Documents/Codex/2026-11-18/https-dsc-capstone-org-2026-27/outputs/bikeshare-open/src/features.py:
[714 rows x 28 columns]

    def test_rolling_mean_excludes_today(feats):
        """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
        by_date = feats.set_index("dteday")[TARGET]
        date = feats.dteday.iloc[200]
        window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
        if all(d in by_date.index for d in window):
            expected = sum(by_date[d] for d in window) / 7
>           assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E           assert np.float64(4389.0) == 4414.857142857143 ï¿½ 0.00441486
E             
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ï¿½ 0.00441486

tests\test_leakage.py:60: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 8 passed in 1.54s

```

Actual repaired test output:
```text
.................                                                        [100%]
17 passed in 3.63s

```

## Silent weather encoder

Exact change:

```diff
-raise ValueError(f"unmapped weather labels: {sorted(unknown)}")
+pass  # seeded fault: silently map unexpected labels to NaN
```

Repair: restore original bytes in finally. One Codex orchestration turn / one scripted restore action; no local-model repair turn. Broken pytest exit 1; hook exit 2; repaired pytest exit 0.

Actual red test output:
```text
............F....                                                        [100%]
================================== FAILURES ===================================
______________________ test_unknown_weather_fails_loudly ______________________

    def test_unknown_weather_fails_loudly():
>       with pytest.raises(ValueError, match="unmapped weather labels"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests\test_leakage.py:73: Failed
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_unknown_weather_fails_loudly - Failed: DID...
1 failed, 16 passed in 3.67s

```

Actual hook stderr:
```text
Leakage tests failed after editing C:/Users/Calvin/Documents/Codex/2026-11-18/https-dsc-capstone-org-2026-27/outputs/bikeshare-open/src/features.py:
.......F.                                                                [100%]
================================== FAILURES ===================================
______________________ test_unknown_weather_fails_loudly ______________________

    def test_unknown_weather_fails_loudly():
>       with pytest.raises(ValueError, match="unmapped weather labels"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests\test_leakage.py:73: Failed
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_unknown_weather_fails_loudly - Failed: DID...
1 failed, 8 passed in 1.44s

```

Actual repaired test output:
```text
.................                                                        [100%]
17 passed in 3.36s

```

## First hook attempt: Windows environment failure

The first forbidden-column run returned pytest exit 1 and hook exit 1, with empty stderr. It did not prove the hook worked, so it was rejected. Windows resolved a bare `bash` subprocess to WSL despite `shutil.which` identifying Git Bash. Passing Git Bash’s resolved absolute executable and a slash-normalized source path fixed the harness. The failed metadata is retained in `docs/evidence/forbidden.json`; the successful rerun above is the evidence used.

## Fourth fault: Bash cp into raw data

A temporary CSV was the original bytes plus one newline. `cp "$1" data/raw/bike_daily.csv` succeeded through Git Bash. The Edit/Write PostToolUse matcher would not run on Bash at all; invoking its script with the Bash payload also returned 0 with empty stderr. This is a real enforcement gap, not a claim that permission denials protect Bash writes. The source was restored in `finally` and the SHA256 rechecked.

```json
{
  "command": "cp \"$1\" data/raw/bike_daily.csv",
  "mutation": "append one newline to an otherwise identical CSV",
  "cp_exit": 0,
  "posttool_hook_exit": 0,
  "posttool_hook_stderr": "",
  "ingest_hash_guard_exit": 1,
  "stop_hook_exit": 2,
  "original_sha256": "a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc",
  "restored_sha256": "a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc"
}

```

Actual ingest hash-guard output:
```text
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\Calvin\Documents\Codex\2026-11-18\https-dsc-capstone-org-2026-27\outputs\bikeshare-open\src\ingest.py", line 42, in <module>
    verify_raw_hash()
  File "C:\Users\Calvin\Documents\Codex\2026-11-18\https-dsc-capstone-org-2026-27\outputs\bikeshare-open\src\ingest.py", line 37, in verify_raw_hash
    raise ValueError(f"raw CSV hash mismatch: expected {RAW_SHA256}, got {actual}")
ValueError: raw CSV hash mismatch: expected a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc, got 8b19181406f2d6599f3cb5bd73ce3e81b5883599ca00badcfdb2f7e17c9dded7

```

Actual Stop hook stderr:
```text
Final verification failed; repair before claiming completion.
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\Calvin\Documents\Codex\2026-11-18\https-dsc-capstone-org-2026-27\outputs\bikeshare-open\src\ingest.py", line 42, in <module>
    verify_raw_hash()
  File "C:\Users\Calvin\Documents\Codex\2026-11-18\https-dsc-capstone-org-2026-27\outputs\bikeshare-open\src\ingest.py", line 37, in verify_raw_hash
    raise ValueError(f"raw CSV hash mismatch: expected {RAW_SHA256}, got {actual}")
ValueError: raw CSV hash mismatch: expected a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc, got 8b19181406f2d6599f3cb5bd73ce3e81b5883599ca00badcfdb2f7e17c9dded7


```

The implemented controls are a SHA256 check in `make data`, an immutable-raw test, and a Stop hook that runs ingest verification and the tests regardless of which editing tool was used. They detect the corruption before the work can be called complete; filesystem permissions would be needed to prevent the write itself.
