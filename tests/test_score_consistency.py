"""Unit tests for the pure (non-network, non-insightface) parts of
scripts/score_consistency.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from score_consistency import build_score_inputs, format_report, load_manual_scores

TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1] / "influencers" / "_template" / "manual_consistency_scores.yaml"
)


def test_load_manual_scores_reads_template():
    scores = load_manual_scores(TEMPLATE_PATH)
    assert set(scores) == {"body_proportion_score", "distinctive_feature_score", "human_review_score"}
    assert all(isinstance(v, float) for v in scores.values())


def test_load_manual_scores_rejects_missing_keys(tmp_path):
    incomplete = tmp_path / "scores.yaml"
    incomplete.write_text("body_proportion_score: 90\n")
    with pytest.raises(ValueError):
        load_manual_scores(incomplete)


def test_build_score_inputs_assembles_correctly():
    manual = {"body_proportion_score": 90.0, "distinctive_feature_score": 85.0, "human_review_score": 80.0}
    inputs = build_score_inputs(face_embedding_score=95.0, manual_scores=manual)
    assert inputs.face_embedding_score == 95.0
    assert inputs.body_proportion_score == 90.0
    assert inputs.distinctive_feature_score == 85.0
    assert inputs.human_review_score == 80.0


def test_format_report_pass_verdict():
    manual = {"body_proportion_score": 90.0, "distinctive_feature_score": 90.0, "human_review_score": 90.0}
    inputs = build_score_inputs(face_embedding_score=90.0, manual_scores=manual)
    report = format_report(90.0, inputs, tier=1)
    assert "PASS" in report
    assert "Tier 1" in report
    assert "proceed to Phase 6" in report


def test_format_report_fail_verdict_mentions_escalation():
    manual = {"body_proportion_score": 60.0, "distinctive_feature_score": 60.0, "human_review_score": 60.0}
    inputs = build_score_inputs(face_embedding_score=60.0, manual_scores=manual)
    report = format_report(60.0, inputs, tier=1)
    assert "FAIL" in report
    assert "Escalate" in report
