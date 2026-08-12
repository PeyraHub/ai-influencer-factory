"""Unit tests for the pure (non-network) parts of scripts/generate_variations.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_variations import ALL_CONSISTENCY_SHOTS, build_shot_requests, estimate_cost
from engine.prompt_engine.schema import IdentityPack

SOFIA_PATH = Path(__file__).resolve().parents[1] / "influencers" / "sofia_01" / "identity_pack.yaml"


def test_all_consistency_shots_has_fifteen_entries():
    # IDENTITY_SYSTEM.md §6 specifies exactly 15 conditions.
    assert len(ALL_CONSISTENCY_SHOTS) == 15


def test_build_shot_requests_overrides_pulid_reference():
    identity = IdentityPack.from_yaml(SOFIA_PATH)
    reference_url = "https://example.com/candidate_007.png"
    requests = build_shot_requests(identity, reference_url, ["selfie", "gym"])

    assert len(requests) == 2
    for _, request in requests:
        assert request.identity.pulid_reference_image == reference_url
        # Everything else about the identity is untouched.
        assert request.identity.trigger_token == identity.trigger_token


def test_build_shot_requests_rejects_unknown_shot():
    identity = IdentityPack.from_yaml(SOFIA_PATH)
    try:
        build_shot_requests(identity, "https://example.com/ref.png", ["not_a_real_shot"])
        assert False, "expected KeyError"
    except KeyError as exc:
        assert "selfie" in str(exc)


def test_build_shot_requests_all_shots_produce_prompts():
    from engine.prompt_engine import build_prompt

    identity = IdentityPack.from_yaml(SOFIA_PATH)
    requests = build_shot_requests(identity, "https://example.com/ref.png", list(ALL_CONSISTENCY_SHOTS))
    assert len(requests) == 15
    for shot_key, request in requests:
        bundle = build_prompt(request)
        assert bundle.positive_prompt  # every shot produces a non-empty prompt


def test_estimate_cost_matches_verified_fal_pricing():
    # fal-ai/flux-pulid: $0.0333/megapixel, 1 billed MP/image at 768x1024
    # (verified 2026-08) -> 15 * 0.0333 = 0.4995.
    cost = estimate_cost(15)
    assert cost == pytest.approx(0.4995)
