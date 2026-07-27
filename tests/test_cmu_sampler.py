from __future__ import annotations

import gzip
import json
from pathlib import Path

from preprocessing.sample_cmu_shards import sample_shards


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def _row(label: str, script: str, token: str) -> dict[str, object]:
    return {
        "lbl": label,
        "wght": 1,
        "dbg": f"{script}:1",
        "feat": {token: 1, "document": 1},
    }


def test_sampler_keeps_positives_samples_negatives_and_excludes_baseline(
    tmp_path: Path,
) -> None:
    baseline = tmp_path / "baseline.jsonl"
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    output = tmp_path / "sample.jsonl.gz"
    _write_jsonl(baseline, [_row("n", "baseline-script", "baseline-token")])
    _write_jsonl(
        first,
        [
            _row("p", "positive-a", "innerhtml"),
            _row("p", "positive-a-copy", "innerhtml"),
            _row("n", "negative-a", "safe-a"),
            _row("n", "negative-b", "safe-b"),
            _row("n", "baseline-script", "new-token"),
        ],
    )
    _write_jsonl(
        second,
        [
            _row("p", "positive-b", "document-write"),
            _row("n", "negative-c", "safe-c"),
            _row("n", "negative-d", "safe-d"),
        ],
    )

    summary = sample_shards(
        [first, second],
        output,
        exclusions=[baseline],
        negative_rows_per_input=1,
        seed=42,
    )
    with gzip.open(output, mode="rt", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]

    assert summary.input_rows == 8
    assert summary.raw_positive_rows == 3
    assert summary.raw_negative_rows == 5
    assert summary.unique_positive_rows == 2
    assert summary.duplicate_positive_features == 1
    assert summary.excluded_negative_baseline_scripts == 1
    assert summary.excluded_positive_baseline_scripts == 0
    assert summary.excluded_positive_baseline_features == 0
    assert summary.sampled_negative_rows == 2
    assert summary.written_rows == 4
    assert sum(row["lbl"] == "p" for row in rows) == 2
    assert sum(row["lbl"] == "n" for row in rows) == 2
    assert all(not str(row["dbg"]).startswith("baseline-script:") for row in rows)


def test_sampler_is_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    first_output = tmp_path / "first.jsonl.gz"
    second_output = tmp_path / "second.jsonl.gz"
    _write_jsonl(
        source,
        [_row("n", f"script-{index}", f"token-{index}") for index in range(20)],
    )

    for output in (first_output, second_output):
        sample_shards(
            [source],
            output,
            exclusions=[],
            negative_rows_per_input=5,
            seed=7,
        )

    assert first_output.read_bytes() == second_output.read_bytes()
