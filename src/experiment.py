"""Validation-first residual-target experiment; test requires an explicit flag."""
import argparse
import json
from pathlib import Path

from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, r2_score

from src.config import TARGET
from src.features import build_features, feature_columns
from src.ingest import load_raw
from src.train import MODELS, temporal_split


def run(split="valid"):
    frame = build_features(load_raw())
    cols = feature_columns(frame)
    train, valid, test = temporal_split(frame)
    part = valid if split == "valid" else test
    model = clone(MODELS["hgb"])
    # Delta from yesterday is known only as a TRAINING target. At inference,
    # yesterday's observed count is the reconstruction anchor, never today's.
    delta = train[TARGET] - train.cnt_lag_1
    model.fit(train[cols], delta)
    prediction = part.cnt_lag_1.to_numpy() + model.predict(part[cols])
    return {
        "transformation": "cnt - cnt_lag_1",
        "reconstruction": "cnt_lag_1 + predicted_delta",
        "split": split,
        "n_train": len(train),
        "n_evaluation": len(part),
        "r2": round(float(r2_score(part[TARGET], prediction)), 4),
        "mae": round(float(mean_absolute_error(part[TARGET], prediction)), 1),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=["valid", "test"], default="valid")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run(args.split)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
