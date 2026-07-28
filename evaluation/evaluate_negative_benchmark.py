from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

import joblib
import numpy as np
from scipy import sparse

from training.train_lightgbm_grouped import (
    ParsedRecord,
    RejectedRecord,
    iter_source_rows,
    parse_record,
)


class ProbabilityModel(Protocol):
    n_features_in_: int

    def predict_proba(self, matrix: sparse.csr_matrix) -> np.ndarray: ...


@dataclass(frozen=True)
class OperatingPoint:
    threshold: float
    true_negatives: int
    false_positives: int
    false_positive_rate: float
    specificity: float


def vectorize_records(
    records: list[ParsedRecord],
    vocabulary: dict[str, int],
) -> tuple[sparse.csr_matrix, int]:
    data: list[float] = []
    columns: list[int] = []
    row_pointer = [0]
    zero_coverage_rows = 0

    for record in records:
        matched = False
        for token, count in record.features.items():
            column = vocabulary.get(token)
            if column is None:
                continue
            columns.append(column)
            data.append(count)
            matched = True
        if not matched:
            zero_coverage_rows += 1
        row_pointer.append(len(data))

    matrix = sparse.csr_matrix(
        (
            np.asarray(data, dtype=np.float32),
            np.asarray(columns, dtype=np.int32),
            np.asarray(row_pointer, dtype=np.int64),
        ),
        shape=(len(records), len(vocabulary)),
        dtype=np.float32,
    )
    return matrix, zero_coverage_rows


def operating_point(scores: np.ndarray, threshold: float) -> OperatingPoint:
    false_positives = int((scores >= threshold).sum())
    true_negatives = int(scores.size - false_positives)
    false_positive_rate = false_positives / scores.size if scores.size else 0.0
    return OperatingPoint(
        threshold=threshold,
        true_negatives=true_negatives,
        false_positives=false_positives,
        false_positive_rate=false_positive_rate,
        specificity=1.0 - false_positive_rate,
    )


def evaluate_negative_benchmark(
    inputs: Iterable[Path],
    model: ProbabilityModel,
    vocabulary: dict[str, int],
    *,
    selected_threshold: float,
    batch_size: int = 4096,
) -> dict[str, object]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if model.n_features_in_ != len(vocabulary):
        raise ValueError(
            "model/vocabulary feature mismatch: "
            f"{model.n_features_in_} != {len(vocabulary)}"
        )

    rejected: Counter[str] = Counter()
    batch: list[ParsedRecord] = []
    score_batches: list[np.ndarray] = []
    parsed_rows = 0
    zero_coverage_rows = 0

    def score_batch() -> None:
        nonlocal zero_coverage_rows
        if not batch:
            return
        matrix, zero_rows = vectorize_records(batch, vocabulary)
        booster = getattr(model, "booster_", None)
        if booster is not None:
            raw_scores = booster.predict(matrix)
        else:
            raw_scores = model.predict_proba(matrix)[:, 1]
        scores = np.asarray(raw_scores, dtype=np.float64)
        score_batches.append(scores)
        zero_coverage_rows += zero_rows
        batch.clear()

    for path, row in iter_source_rows(inputs):
        record = parse_record(path, row)
        if isinstance(record, RejectedRecord):
            rejected[record.reason] += 1
            continue
        if record.label:
            raise ValueError(
                "negative benchmark contains a positive row: "
                f"{record.source_file}:{record.dbg}"
            )
        batch.append(record)
        parsed_rows += 1
        if len(batch) >= batch_size:
            score_batch()
    score_batch()

    if not score_batches:
        raise ValueError("benchmark contains no valid rows")

    scores = np.concatenate(score_batches)
    percentiles = {
        str(percentile): float(np.percentile(scores, percentile))
        for percentile in (0, 50, 90, 95, 99, 99.9, 100)
    }
    return {
        "benchmark_type": "external_unique_negative_corpus",
        "rows": parsed_rows,
        "rejected_rows": dict(rejected),
        "zero_vocabulary_coverage_rows": zero_coverage_rows,
        "vocabulary_coverage_rate": 1.0 - (zero_coverage_rows / parsed_rows),
        "score_summary": {
            "mean": float(scores.mean()),
            "percentiles": percentiles,
        },
        "selected_threshold": asdict(
            operating_point(scores, selected_threshold)
        ),
        "threshold_0_5": asdict(operating_point(scores, 0.5)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Measure false-positive rates on an external corpus containing only "
            "previously unseen negative DOM-XSS feature bags."
        )
    )
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--vocabulary", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=4096)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = joblib.load(args.model)
    vocabulary = json.loads(args.vocabulary.read_text(encoding="utf-8"))
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    selected_threshold = float(
        metadata["training"]["validation_selected_threshold"]
    )
    result = evaluate_negative_benchmark(
        args.inputs,
        model,
        vocabulary,
        selected_threshold=selected_threshold,
        batch_size=args.batch_size,
    )
    result["artifacts"] = {
        "model": str(args.model),
        "vocabulary": str(args.vocabulary),
        "metadata": str(args.metadata),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
