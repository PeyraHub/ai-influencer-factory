"""Unit tests for the pure (non-network) parts of scripts/generate_candidates.py."""
import sys
from pathlib import Path

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


def test_estimate_cost_matches_costs_md_ballpark():
    # COSTS.md quotes ~EUR 1-2 for ~40 zero-shot exploration images.
    cost = estimate_cost(40)
    assert 0.5 <= cost <= 2.0
