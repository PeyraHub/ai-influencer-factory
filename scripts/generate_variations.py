#!/usr/bin/env python3
"""Phase 2, steps 4 & 6 — zero-shot identity-conditioned variations.

Two uses of the same script, per docs/PHASE2_RUNBOOK.md:
  (a) cheap shortlist check — a handful of shots per shortlisted candidate,
      to eliminate ones that don't hold up before spending on the full test
  (b) the full 15-shot Character Consistency Test (IDENTITY_SYSTEM.md §6) on
      the ONE final chosen candidate, whose output feeds score_consistency.py

Both use fal-ai/flux-pulid: zero-shot identity conditioning on a single
reference image, no training (Tier 1 of the Progressive Identity Complexity
Ladder, IDENTITY_SYSTEM.md §2a). Only escalate past this script's output if
score_consistency.py says Tier 1 didn't clear 80/100.

Usage:
    pip install -e ".[generation]"
    python scripts/generate_variations.py \
        --identity influencers/sofia_01/identity_pack.yaml \
        --reference influencers/sofia_01/versions/v1/candidates/candidate_007.png \
        --shots selfie,professional,smiling                      # cheap shortlist check
    python scripts/generate_variations.py \
        --identity influencers/sofia_01/identity_pack.yaml \
        --reference influencers/sofia_01/versions/v1/canonical_refs/canonical_front.png \
        --shots all --out-dir influencers/sofia_01/versions/v1/consistency_test  # full test

Spend is capped: see engine/budget_guard.py. Shares the same "tier1" ledger
label (and file) as generate_candidates.py, so the whole Tier 1 attempt
(candidate sweep + shortlist checks + full test) is capped together —
default EUR 3.00 (docs/PHASE2_RUNBOOK.md), override with --cap-eur, exceed
only with --i-authorize-overage after explicit owner approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.budget_guard import BudgetCapExceeded, Ledger, DEFAULT_CAP_EUR
from engine.prompt_engine import GenerationRequest, build_prompt
from engine.prompt_engine.schema import IdentityPack

# fal-ai/flux-pulid: $0.0333 / megapixel, billed rounded up to the nearest
# megapixel (fal.ai pricing docs, verified 2026-08). Same explicit-resolution
# reasoning as generate_candidates.py — see that file's comment for why.
IMAGE_WIDTH = 768
IMAGE_HEIGHT = 1024
BILLED_MEGAPIXELS_PER_IMAGE = 1  # ceil(768*1024 / 1_000_000) = ceil(0.786) = 1
FLUX_PULID_PRICE_PER_MEGAPIXEL_EUR = 0.0333
FLUX_PULID_PRICE_PER_IMAGE = round(BILLED_MEGAPIXELS_PER_IMAGE * FLUX_PULID_PRICE_PER_MEGAPIXEL_EUR, 4)

# The 15 conditions of the Character Consistency Test, IDENTITY_SYSTEM.md §6,
# each mapped to a (scene, photo_style) pair the prompt engine understands.
ALL_CONSISTENCY_SHOTS: dict[str, tuple[str, str]] = {
    "selfie": ("selfie, looking at camera", "iphone_selfie"),
    "gym": ("at the gym, mid-workout", "gym_photo"),
    "beach": ("at the beach in a bikini", "beach"),
    "evening_dress": ("wearing an evening dress, night out", "nightlife"),
    "hoodie_casual": ("wearing a hoodie, relaxed casual day", "home_morning"),
    "restaurant": ("having dinner at a restaurant", "restaurant"),
    "airport": ("at the airport, traveling", "travel"),
    "professional": ("professional portrait", "professional_campaign"),
    "night_photo": ("night out photo", "nightlife"),
    "full_body": ("full body standing portrait", "iphone_selfie"),
    "close_up": ("close-up portrait", "professional_campaign"),
    "profile": ("profile view portrait", "iphone_selfie"),
    "smiling": ("smiling warmly", "iphone_selfie"),
    "serious": ("serious, neutral expression", "professional_campaign"),
    "hair_tied": ("hair tied back, workout ready", "gym_photo"),
}


def build_shot_requests(
    identity: IdentityPack, reference_image_url: str, shot_keys: list[str]
) -> list[tuple[str, GenerationRequest]]:
    """Pure function: resolves shot keys to (scene, style) and builds requests
    with PuLID conditioning pointed at the given reference. No network I/O."""
    unknown = [k for k in shot_keys if k not in ALL_CONSISTENCY_SHOTS]
    if unknown:
        known = ", ".join(sorted(ALL_CONSISTENCY_SHOTS))
        raise KeyError(f"Unknown shot(s) {unknown}. Known shots: {known}")

    # PuLID conditioning is applied via the identity's pulid_reference_image
    # field — override it to point at THIS reference (the candidate being
    # tested), not whatever the Identity Pack currently has on file.
    conditioned_identity = IdentityPack(
        **{**identity.__dict__, "pulid_reference_image": reference_image_url}
    )

    requests = []
    for key in shot_keys:
        scene, style = ALL_CONSISTENCY_SHOTS[key]
        request = GenerationRequest(identity=conditioned_identity, scene=scene, photo_style=style)
        requests.append((key, request))
    return requests


def estimate_cost(shot_count: int, price_per_image: float = FLUX_PULID_PRICE_PER_IMAGE) -> float:
    return round(shot_count * price_per_image, 4)


def generate_and_save(
    requests: list[tuple[str, GenerationRequest]],
    reference_path: str,
    api_key: str,
    out_dir: Path,
    ledger: Ledger,
    cap_eur: float = DEFAULT_CAP_EUR,
    authorize_overage: bool = False,
) -> list[dict]:
    """Network I/O — requires the 'generation' extra (fal-client) and a real API key."""
    try:
        import fal_client
    except ImportError as exc:
        raise ImportError(
            "generate_and_save requires the 'generation' extra: pip install -e '.[generation]'"
        ) from exc

    import os
    import urllib.request

    os.environ.setdefault("FAL_KEY", api_key)
    out_dir.mkdir(parents=True, exist_ok=True)

    reference_url = fal_client.upload_file(reference_path)
    results = []

    for shot_key, request in requests:
        ledger.reserve(FLUX_PULID_PRICE_PER_IMAGE, cap_eur=cap_eur, authorize_overage=authorize_overage)

        bundle = build_prompt(request)
        handle = fal_client.submit(
            "fal-ai/flux-pulid",
            arguments={
                "prompt": bundle.positive_prompt,
                "reference_image_url": reference_url,
                "image_size": {"width": IMAGE_WIDTH, "height": IMAGE_HEIGHT},
            },
        )
        result = handle.get()
        image_url = result["images"][0]["url"]

        image_path = out_dir / f"{shot_key}.png"
        urllib.request.urlretrieve(image_url, image_path)

        metadata = {
            "shot": shot_key,
            "photo_style": request.photo_style,
            "reference_image": reference_path,
            "prompt": bundle.positive_prompt,
            "image_path": str(image_path),
            "estimated_cost_eur": FLUX_PULID_PRICE_PER_IMAGE,
        }
        (out_dir / f"{shot_key}.json").write_text(json.dumps(metadata, indent=2))
        results.append(metadata)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--identity", required=True, type=Path)
    parser.add_argument("--reference", required=True, help="Path to the candidate/canonical reference image")
    parser.add_argument(
        "--shots", required=True, help="Comma-separated shot keys, or 'all' for the full 15-shot Consistency Test"
    )
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cap-eur", type=float, default=DEFAULT_CAP_EUR, help="Hard spend cap for the 'tier1' ledger label")
    parser.add_argument(
        "--i-authorize-overage",
        action="store_true",
        help="Explicit owner authorization to exceed --cap-eur. Do not pass this by default.",
    )
    args = parser.parse_args()

    identity = IdentityPack.from_yaml(args.identity)
    shot_keys = list(ALL_CONSISTENCY_SHOTS) if args.shots == "all" else [s.strip() for s in args.shots.split(",")]
    requests = build_shot_requests(identity, args.reference, shot_keys)

    cost = estimate_cost(len(shot_keys))
    print(f"Identity: {identity.codename} | shots: {len(shot_keys)} | estimated cost: EUR {cost}")

    if args.dry_run:
        for shot_key, request in requests:
            print(f"  {shot_key} (style={request.photo_style}) -> {build_prompt(request).positive_prompt[:90]}...")
        return

    import os

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        print("ERROR: FAL_KEY not set. Copy .env.example to .env and fill it in.", file=sys.stderr)
        sys.exit(1)

    out_dir = args.out_dir or (
        Path("influencers") / identity.codename.lower() / "versions" / "v1" / "variations"
    )
    ledger = Ledger(path=out_dir.parent / ".spend_ledger.json", label="tier1")

    try:
        results = generate_and_save(
            requests, args.reference, api_key, out_dir, ledger, cap_eur=args.cap_eur,
            authorize_overage=args.i_authorize_overage,
        )
    except BudgetCapExceeded as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Saved {len(results)} shots to {out_dir} (tier1 ledger total: EUR {ledger.spent():.2f})")


if __name__ == "__main__":
    main()
