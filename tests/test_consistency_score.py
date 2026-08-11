import pytest

from engine.identity.consistency_score import (
    ConsistencyScoreInputs,
    PASS_THRESHOLD,
    combine_identity_score,
    passes_gate,
)


def test_combine_identity_score_weights_face_embedding_most_heavily():
    high_face = ConsistencyScoreInputs(
        face_embedding_score=100, body_proportion_score=0, distinctive_feature_score=0, human_review_score=0
    )
    high_other = ConsistencyScoreInputs(
        face_embedding_score=0, body_proportion_score=100, distinctive_feature_score=100, human_review_score=0
    )

    assert combine_identity_score(high_face) == pytest.approx(40.0)
    assert combine_identity_score(high_other) == pytest.approx(40.0)


def test_combine_identity_score_perfect_inputs():
    perfect = ConsistencyScoreInputs(100, 100, 100, 100)
    assert combine_identity_score(perfect) == pytest.approx(100.0)


def test_combine_identity_score_rejects_out_of_range():
    with pytest.raises(ValueError):
        combine_identity_score(ConsistencyScoreInputs(101, 0, 0, 0))
    with pytest.raises(ValueError):
        combine_identity_score(ConsistencyScoreInputs(0, -1, 0, 0))


def test_passes_gate_threshold():
    assert passes_gate(PASS_THRESHOLD) is True
    assert passes_gate(PASS_THRESHOLD - 0.01) is False


def test_passes_gate_realistic_borderline_case():
    # Strong face match, but human reviewer flags something off -> still fails the gate.
    borderline = ConsistencyScoreInputs(
        face_embedding_score=95, body_proportion_score=70, distinctive_feature_score=60, human_review_score=50
    )
    score = combine_identity_score(borderline)
    assert score == pytest.approx(74.0)
    assert passes_gate(score) is False
