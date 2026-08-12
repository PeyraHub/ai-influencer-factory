"""Unit tests for the pure (non-network) parts of scripts/generate_candidates.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_candidates import build_candidate_requests, estimate_cost
from engine.prompt_engine.schema import IdentityPack

SOFIA_PATH = Path(__file__).resolve().parents[1] / "influencers" / "sofia_01" / "identity_pack.yaml"


def test_build_candidate_requests_cycles_styles():
    identity = IdentityPack.from_yaml(SOFIA_PATH)
    styles = ["iphone_selfie", "professional_campaign"]
    requests = build_candidate_requests(identity, styles, count=5, seed_start=100)

    assert len(requests) == 5
    seeds = [seed for seed, _ in requests]
    assert seeds == [100, 101, 102, 103, 104]
    assigned_styles = [r.photo_style for _, r in requests]
    assert assigned_styles == ["iphone_selfie", "professional_campaign", "iphone_selfie", "professional_campaign", "iphone_selfie"]


def test_build_candidate_requests_no_identity_conditioning_leak():
    # Phase 2 sweep is plain text-to-image — must not accidentally reference
    # a LoRA/PuLID that doesn't exist yet (see docs/PHASE2_RUNBOOK.md).
    identity = IdentityPack.from_yaml(SOFIA_PATH)
    _, request = build_candidate_requests(identity, ["iphone_selfie"], count=1)[0]
    assert request.outfit is None
    assert request.location is None


def test_build_candidate_requests_rejects_zero_count():
    identity = IdentityPack.from_yaml(SOFIA_PATH)
    try:
        build_candidate_requests(identity, ["iphone_selfie"], count=0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_estimate_cost_matches_verified_fal_pricing():
    # fal-ai/flux/schnell: $0.003/megapixel, 1 billed MP/image at 768x1024
    # (verified 2026-08, see module docstring/comments) -> 40 * 0.003 = 0.12.
    cost = estimate_cost(40)
    assert cost == pytest.approx(0.12)


def test_estimate_cost_full_tier1_attempt_stays_well_under_cap():
    # Sweep (40) + shortlist checks (5 candidates x 3 shots) + full 15-shot
    # test should total well under the EUR 3 Tier 1 cap (engine/budget_guard.py).
    from generate_variations import estimate_cost as variations_cost

    total = estimate_cost(40) + variations_cost(5 * 3) + variations_cost(15)
    assert total < 3.0
