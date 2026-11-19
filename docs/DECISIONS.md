# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

- 2026-11-18 — Codex automation: retain the five starter decisions above as inherited context, not claims of work performed by the group. Starter `make all` and its fixed holdout smoke test ran for setup; before-feature test metrics are sealed until feature/transformation choices are fixed. No test metric is used for selection.
- 2026-11-18 — Codex automation: classify all raw input columns in config and add a schema test, plus independent numerical target-identity and unknown-weather checks; this covers new names and encoder faults that the original denylist alone cannot catch. 17 tests pass.
- 2026-11-18 — Codex automation: preselect the target transformation `cnt - cnt_lag_1`, reconstructed with yesterday's count, to remove the level trend without learning from future rows. Initial validation-only R2 0.6079 and MAE 834.3, before the new feature. Keep the untransformed models as the main comparison.
- 2026-11-18 — Codex automation: add `/seed-fault` to CLAUDE.md and keep the other inherited constraints; use one reusable scripted demonstration rather than fabricate model repair conversations. Group review of these automated methodological choices is still required.
