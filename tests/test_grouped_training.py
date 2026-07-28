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


def test_capped_duplicate_indexes_keep_bounded_repetition() -> None:
    import numpy as np

    indexes = np.asarray([0, 1, 2, 3, 4])
    hashes = np.asarray(["a", "a", "a", "b", "b"])

    assert MODULE.capped_duplicate_indexes(indexes, hashes, 2).tolist() == [0, 1, 3, 4]


def test_security_interaction_features_are_added() -> None:
    features = MODULE.normalize_feature_mapping(
        "{'location': 1, 'hash': 1, 'innerHTML': 1}"
    )

    assert features is not None
    assert features["sec_source_url"] == 1.0
    assert features["sec_sink_inner_html"] == 1.0
    assert features["sec_pair_url_inner_html"] == 1.0


def test_source_without_sink_has_no_pair_feature() -> None:
    features = MODULE.normalize_feature_mapping("{'location': 1, 'hash': 1}")

    assert features is not None
    assert features["sec_source_url"] == 1.0
    assert not any(token.startswith("sec_pair_") for token in features)


def test_target_recall_threshold_uses_highest_eligible_score() -> None:
    import numpy as np

    labels = np.asarray([1, 1, 0, 0])
    scores = np.asarray([0.9, 0.7, 0.8, 0.1])

    threshold = MODULE.target_recall_threshold(labels, scores, 1.0)

    assert threshold == 0.7


def test_classification_metrics_report_accuracy_from_confusion_counts() -> None:
    import numpy as np

    metrics = MODULE.classification_metrics(
        np.asarray([1, 1, 0, 0]),
        np.asarray([0.9, 0.4, 0.8, 0.1]),
        0.5,
    )

    assert metrics["accuracy"] == 0.5
    assert metrics["confusion"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}
