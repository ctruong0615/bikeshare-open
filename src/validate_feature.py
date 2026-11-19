"""Compare the proposed feature using validation scores only."""
import json
from pathlib import Path

from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, r2_score

from src.config import TARGET
from src.features import build_features, feature_columns
from src.ingest import load_raw
from src.train import MODELS, temporal_split


def run():
    frame = build_features(load_raw())
    train, valid, _ = temporal_split(frame)
    all_cols = feature_columns(frame)
    result = {}
    for scenario in ("before", "after"):
        cols = [c for c in all_cols if scenario == "after" or c != "cnt_roll_std_7"]
        scores = {}
        for name, estimator in MODELS.items():
            model = clone(estimator).fit(train[cols], train[TARGET])
            prediction = model.predict(valid[cols])
            scores[name] = {
                "r2": round(float(r2_score(valid[TARGET], prediction)), 4),
                "mae": round(float(mean_absolute_error(valid[TARGET], prediction)), 1),
            }
        result[scenario] = scores
    return result


if __name__ == "__main__":
    result = run()
    path = Path("reports/validation_feature.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
