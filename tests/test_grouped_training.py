from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "training" / "train_lightgbm_grouped.py"
SPEC = importlib.util.spec_from_file_location("grouped_training", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_split_is_deterministic_and_script_level() -> None:
    first = MODULE.split_for_script("script-123")
    second = MODULE.split_for_script("script-123")

    assert first == second
    assert first in {0, 1, 2}


def test_feature_hash_ignores_mapping_order_and_case() -> None:
    first = MODULE.normalize_feature_mapping("{'Document': 1, 'write': 2}")
    second = MODULE.normalize_feature_mapping("{'write': 2, 'document': 1}")

    assert first is not None and second is not None
    assert MODULE.canonical_feature_hash(first) == MODULE.canonical_feature_hash(second)


def test_invalid_or_negative_counts_are_rejected() -> None:
    assert MODULE.normalize_feature_mapping("{'document': -1}") is None
    assert MODULE.normalize_feature_mapping("not a mapping") is None


def test_unique_indexes_remove_exact_feature_duplicates() -> None:
    import numpy as np

    indexes = np.asarray([0, 1, 2, 3])
    hashes = np.asarray(["a", "a", "b", "c"])

    assert MODULE.unique_indexes(indexes, hashes).tolist() == [0, 2, 3]
