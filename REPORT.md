# Results

We evaluated one-step daily bikeshare demand using the provided processed mirror: 728 raw rows covering 2011-01-03 through 2012-12-31, with 2011-03-10 absent. Reindexing before lagging preserves calendar meaning. Seven warm-up days and seven downstream days lost to the absent observation leave 714 usable rows: 348 training rows in 2011, 182 validation rows in H1 2012, and 184 test rows in H2 2012. Both feature scenarios use identical rows. The mean baseline is fitted on training only; persistence uses yesterday’s observed count, representing daily rolling forecasts rather than one fixed-origin six-month forecast.

| Feature set | Model | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---|---:|---:|---:|---:|
| Before | baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Before | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Before | ridge | 0.6475 | 832.9 | 0.5833 | 947.1 |
| Before | hgb | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| After | baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| After | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| After | ridge | 0.7224 | 700.4 | 0.6356 | 840.3 |
| After | hgb | 0.0977 | 1381.6 | -0.6959 | 2108.4 |

These eight rows are generated from `reports/metrics.json`: its top-level scores are the final feature set, and `before_feature` contains the comparison without `cnt_roll_std_7`. `make all` regenerates both scenarios rather than trusting copied historical metrics. MAE is measured in rides. Dependencies and estimator settings remain pinned to the starter. `make test` currently passes 19 tests. Fault evidence, including the feature’s genuinely failing pre-implementation test, is pasted in `docs/SEEDED_FAULTS.md`.

The SDK self-auditor completed a real local-model run and reported no leakage, valid temporal ordering, both baselines, and reproducibility. Its five `findings` describe passing behavior rather than defects, so we treat them as confirmations, not five problems to fix. The actual trace contained nine Read calls and thirteen Bash calls, with seven failed tool results and no custom `check_identity` invocation. Its high confidence overstates that verification: the independent numerical-identity test and clean-checkout reproduction carry the evidence. It also did not flag the realized-weather deployment limitation discussed below. The trace summary is in `docs/evidence/sdk-audit-verification.json`.

The added feature is the sample standard deviation of counts from d−7 through d−1. All seven counts are observed before d; the builder reindexes first and applies `shift(1)` before `rolling(7).std(ddof=1)`. The named-date test independently computes sample variability for Jan 10 from the seven preceding raw observations. No longer warm-up is needed. We kept the feature using ridge’s validation improvement of +0.0749 R² and −132.5 MAE. Gradient boosting deteriorated by −0.1208 validation R²; we did not conceal that result or select a different feature using test scores.

# Headline finding

The intentionally leaky model achieved R² = 1.000000 because `casual + registered == cnt`; it learned an unavailable arithmetic identity. With forbidden columns excluded and a temporal split, the training-mean baseline scores −2.1441 test R², exposing the large change in demand level. Before the feature, ridge scores 0.5833 versus persistence at 0.5099, but loses on MAE (947.1 versus 840.1 rides). After adding historical variability, ridge reaches 0.6356 test R² and 840.3 MAE, while untransformed gradient boosting falls to −0.6959 R² and 2108.4 MAE. A negative score still beats the mean baseline here: negative R² is not synonymous with losing every baseline. We retained the feature because it helped ridge on validation, and report the tree’s decline alongside it.

The result is a retrospective benchmark, with an important deployment limitation: the starter uses realized same-day weather. A true day-ahead service would require archived weather forecasts or a different information cutoff, followed by fresh evaluation. Historical demand features are available only after the preceding day closes. These qualifications prevent treating the benchmark as evidence that the current system is ready to deploy.

# Exercise 4: target transformation

We preselected the residual target `cnt - cnt_lag_1`, fitted the same fixed gradient-boosting model on training rows only, and reconstructed each prediction as yesterday’s observed count plus the predicted residual. This moves the changing demand level into an available anchor, allowing the tree to predict deviations rather than extrapolate the entire level. There is no target-derived input from the day being predicted and no fit on validation or test data. The experiment is reproducible with `python -m src.experiment`; test scoring requires `--split test`.

With original features, residual-target validation R² was 0.6079 and MAE 834.3, compared with untransformed hgb at 0.2185 and 1296.6. With the final feature set, the locked transformation yielded validation R² 0.5642 and MAE 885.8 versus untransformed hgb at 0.0977 and 1381.6; it still trailed final ridge (0.7224, 700.4). The final test result was 0.4761 R² and 990.5 MAE, much better than untransformed hgb but worse than persistence and ridge. This makes the tree more competitive, not the winner. We consider the transformation defensible for sequential one-day forecasts, subject to the weather limitation, rather than a reason to keep searching for a winning test result. The main committed metrics remain untransformed.

Feature and transformation choices were locked in commit 39e16ea before final holdout scoring. The initial setup ran the starter pipeline, generating test metrics without inspecting them for selection; the inherited test suite also contains a fixed holdout-performance smoke assertion, run repeatedly. We therefore do not claim that the test set was never accessed. Final test scores were inspected only after choices were fixed; subsequent pipeline runs check reproducibility, not tuning.

# Exercise 5: ridge vs persistence

For the original pipeline, ridge’s test R² advantage is 0.0734, while MAE is 107.0 rides worse than persistence (947.1 versus 840.1). That evidence does not justify deployment for a goal of minimizing typical absolute daily error: the free persistence rule is simpler and wins on that metric. Our final ridge improves the squared-error objective further (R² 0.6356 versus 0.5099), but its MAE remains 0.2 rides worse (840.3 versus 840.1), effectively a tie at the reported precision. We would retain persistence as the operational default until the group specifies whether large errors deserve disproportionate cost and obtains more rolling-origin evidence. If squared error is the actual cost, ridge is a reasonable candidate for further evaluation; one temporal holdout and realized-weather inputs are insufficient deployment evidence.

# Attribution

Models used: local `qwen3.5:9b` via Ollama as `bikeshare-coder`, 65,536-token context, and Codex (the coding agent in this chat; exact backend model size is not exposed). This was a mixed-agent workflow, not an exclusively local-model run: Codex handled most implementation and analysis. No alternative Ollama model size was substituted.

Agent-generated work:
- Codex created the repository history, corrected and added tests, implemented the feature, validation and residual-target experiments, integrity/Stop checks, fault scripts and evidence, SDK adjustments, and this report draft. The main modelling pipeline, baseline choices, and five initial decision lines were inherited from the starter.
- Local qwen received the real `/new-feature` invocation. Its attempted test replacement was rejected and preserved; it was not credited with the corrected test or feature. The completed local SDK self-audit result is stored verbatim in `reports/audit.jsonl`.
- Source-fault repairs were scripted byte restorations, one repair action each. They are not measurements of independent qwen debugging performance.
- A real local `/seed-fault` repeat completed successfully in six CLI turns with red pytest exit 1, hook exit 2, and repaired pytest exit 0. An earlier four-turn invocation completed the underlying script but hit its turn limit during follow-up; both outputs are retained. The successful summary named the original evidence paths rather than the new attempt-2 files, so the script now returns an explicit `evidence_prefix` for reliable reporting.

Human decisions and review:
- The user confirmed group submissions are allowed and authorized automation. The request to automate does not establish that group members personally chose every methodological detail.
- Feature retention, target transformation, and interpretation above are agent-proposed decisions recorded in `docs/DECISIONS.md`. The group must review and own these claims before submitting, and record any actual changes it decides to make. No teammate contributions or researcher decisions have been invented.
- Under the instructor's team clarification, Exercise 3 uses pre-merge audits of members' branches in this shared repository. Calvin has accepted the audit of Faline's target-reconstruction branch; `docs/AUDIT.md` contains the verbatim auditor output, checks and accepted verdict. Faline's audit of Andrew and Andrew's audit of Calvin are still pending. A separate all-member report review is recommended, not a named assignment deliverable.
