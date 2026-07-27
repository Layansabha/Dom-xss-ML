from __future__ import annotations

import argparse
import gzip
import io
import json
import random
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TextIO

from training.train_lightgbm_grouped import (
    ParsedRecord,
    RejectedRecord,
    iter_source_rows,
    parse_record,
)


@dataclass(frozen=True)
class SampleSummary:
    input_rows: int
    positive_rows: int
    negative_candidates: int
    sampled_negative_rows: int
    written_rows: int
    excluded_baseline_scripts: int
    excluded_baseline_features: int
    duplicate_positive_features: int
    duplicate_or_conflicting_negatives: int
    rejected_rows: dict[str, int]
    inputs: list[str]
    exclusions: list[str]
    seed: int
    negative_rows_per_input: int


def _payload(record: ParsedRecord) -> dict[str, object]:
    return {
        "lbl": "p" if record.label else "n",
        "wght": record.weight,
        "dbg": record.dbg,
        "feat": record.features,
        "source_file": record.source_file,
    }


def _compact_json(record: ParsedRecord) -> str:
    return json.dumps(
        _payload(record),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def collect_exclusions(paths: Iterable[Path]) -> tuple[set[str], set[str]]:
    scripts: set[str] = set()
    feature_hashes: set[str] = set()
    for path, row in iter_source_rows(paths):
        record = parse_record(path, row)
        if isinstance(record, RejectedRecord):
            continue
        scripts.add(record.script_id)
        feature_hashes.add(record.feature_hash)
    return scripts, feature_hashes


def _deterministic_gzip_text(path: Path) -> TextIO:
    raw = path.open("wb")
    compressed = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
    return io.TextIOWrapper(compressed, encoding="utf-8", newline="\n")


def sample_shards(
    inputs: list[Path],
    output: Path,
    *,
    exclusions: list[Path],
    negative_rows_per_input: int,
    seed: int,
) -> SampleSummary:
    if negative_rows_per_input <= 0:
        raise ValueError("negative_rows_per_input must be positive")

    excluded_scripts, excluded_hashes = collect_exclusions(exclusions)
    positive_records: dict[str, str] = {}
    negative_reservoirs: list[list[tuple[str, str]]] = []
    rejected: Counter[str] = Counter()
    input_rows = 0
    positive_rows = 0
    negative_candidates = 0
    excluded_baseline_scripts = 0
    excluded_baseline_features = 0
    duplicate_positive_features = 0

    for input_index, input_path in enumerate(inputs):
        rng = random.Random(seed + input_index)
        reservoir: list[tuple[str, str]] = []
        input_negative_candidates = 0

        for path, row in iter_source_rows([input_path]):
            input_rows += 1
            record = parse_record(path, row)
            if isinstance(record, RejectedRecord):
                rejected[record.reason] += 1
                continue
            if record.script_id in excluded_scripts:
                excluded_baseline_scripts += 1
                continue
            if record.feature_hash in excluded_hashes:
                excluded_baseline_features += 1
                continue

            serialized = _compact_json(record)
            if record.label:
                positive_rows += 1
                if record.feature_hash in positive_records:
                    duplicate_positive_features += 1
                else:
                    positive_records[record.feature_hash] = serialized
                continue

            input_negative_candidates += 1
            negative_candidates += 1
            candidate = (record.feature_hash, serialized)
            if len(reservoir) < negative_rows_per_input:
                reservoir.append(candidate)
            else:
                replacement = rng.randrange(input_negative_candidates)
                if replacement < negative_rows_per_input:
                    reservoir[replacement] = candidate

            if input_rows % 250_000 == 0:
                print(
                    f"processed {input_rows:,} rows; "
                    f"kept {len(positive_records):,} unique positives"
                )

        negative_reservoirs.append(reservoir)

    output.parent.mkdir(parents=True, exist_ok=True)
    seen_hashes = set(excluded_hashes)
    seen_hashes.update(positive_records)
    sampled_negative_rows = 0
    duplicate_or_conflicting_negatives = 0

    with _deterministic_gzip_text(output) as handle:
        for serialized in positive_records.values():
            handle.write(f"{serialized}\n")
        for reservoir in negative_reservoirs:
            for feature_hash, serialized in reservoir:
                if feature_hash in seen_hashes:
                    duplicate_or_conflicting_negatives += 1
                    continue
                seen_hashes.add(feature_hash)
                sampled_negative_rows += 1
                handle.write(f"{serialized}\n")

    summary = SampleSummary(
        input_rows=input_rows,
        positive_rows=positive_rows,
        negative_candidates=negative_candidates,
        sampled_negative_rows=sampled_negative_rows,
        written_rows=len(positive_records) + sampled_negative_rows,
        excluded_baseline_scripts=excluded_baseline_scripts,
        excluded_baseline_features=excluded_baseline_features,
        duplicate_positive_features=duplicate_positive_features,
        duplicate_or_conflicting_negatives=duplicate_or_conflicting_negatives,
        rejected_rows=dict(rejected),
        inputs=[str(path) for path in inputs],
        exclusions=[str(path) for path in exclusions],
        seed=seed,
        negative_rows_per_input=negative_rows_per_input,
    )
    summary_path = output.with_suffix(f"{output.suffix}.summary.json")
    summary_path.write_text(
        json.dumps(asdict(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output} ({summary.written_rows:,} rows)")
    print(f"wrote {summary_path}")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Stream CMU confirmed-data shards, retain every positive feature bag, "
            "and take a deterministic negative reservoir sample per shard."
        )
    )
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--exclude",
        nargs="*",
        type=Path,
        default=[],
        help="Existing XLSX/JSONL data whose scripts and feature bags must be excluded.",
    )
    parser.add_argument("--negative-rows-per-input", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_shards(
        args.inputs,
        args.output,
        exclusions=args.exclude,
        negative_rows_per_input=args.negative_rows_per_input,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
