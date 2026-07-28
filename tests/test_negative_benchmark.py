from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import sparse

from evaluation.evaluate_negative_benchmark import (
    evaluate_negative_benchmark,
    operating_point,
)


class FakeModel:
    n_features_in_ = 2

    def predict_proba(self, matrix: sparse.csr_matrix) -> np.ndarray:
        scores = np.asarray(matrix[:, 0].toarray()).ravel() / 10
        return np.column_stack((1 - scores, scores))


def _write_rows(path: Path, labels: list[str]) -> None:
    rows = [
        {
            "lbl": label,
            "wght": 1,
            "dbg": f"script-{index}:1",
            "feat": {"known": index + 1},
        }
        for index, label in enumerate(labels)
    ]
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_negative_benchmark_reports_false_positive_rate(tmp_path: Path) -> None:
    source = tmp_path / "negative.jsonl"
    _write_rows(source, ["n", "n", "n"])

    result = evaluate_negative_benchmark(
        [source],
        FakeModel(),
        {"known": 0, "other": 1},
        selected_threshold=0.25,
        batch_size=2,
    )

    selected = result["selected_threshold"]
    assert result["rows"] == 3
    assert result["zero_vocabulary_coverage_rows"] == 0
    assert selected["false_positives"] == 1
    assert selected["true_negatives"] == 2
    assert selected["false_positive_rate"] == 1 / 3


def test_negative_benchmark_rejects_positive_rows(tmp_path: Path) -> None:
    source = tmp_path / "mixed.jsonl"
    _write_rows(source, ["n", "p"])

    try:
        evaluate_negative_benchmark(
            [source],
            FakeModel(),
            {"known": 0, "other": 1},
            selected_threshold=0.5,
        )
    except ValueError as exc:
        assert "positive row" in str(exc)
    else:
        raise AssertionError("positive row was accepted")


def test_operating_point_handles_empty_scores() -> None:
    point = operating_point(np.asarray([]), 0.5)
    assert point.false_positive_rate == 0
    assert point.specificity == 1
