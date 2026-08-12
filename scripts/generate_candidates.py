#!/usr/bin/env python3
"""Phase 2, step 2 — wide zero-shot candidate face sweep.

See docs/PHASE2_RUNBOOK.md for the full procedure this script is one step
of. No identity conditioning here on purpose: there is no reference face yet
to condition on, so this is plain text-to-image from the Identity Pack's
descriptor_fragments, varied across style/seed for real diversity.

IMPORTANT — run a 1-2 image test first: `--count 2`, inspect the output,
THEN run the full `--count 40`. This is the literal first command in
docs/PHASE2_RUNBOOK.md step 2, not optional. The spend cap below tracks
cumulative cost across both invocations, so the small test's cost still
counts against the Tier 1 budget.

Usage:
    pip install -e ".[generation]"   # adds fal-client, only needed for this script
    cp .env.example .env             # fill in FAL_KEY
    python scripts/generate_candidates.py \
        --identity influencers/sofia_01/identity_pack.yaml --count 2    # sanity check first
    python scripts/generate_candidates.py \
        --identity influencers/sofia_01/identity_pack.yaml --count 40   # then the full sweep

The request-building logic (build_candidate_requests, estimate_cost) is pure
and unit-tested without network access — see tests/test_generate_candidates.py.
Only the actual fal.ai call requires the optional 'generation' extra and a
funded account.

Spend is capped: see engine/budget_guard.py. Every call reserves its
estimated cost against influencers/<codename>/versions/v1/.spend_ledger.json
under the "tier1" label before hitting the network; once cumulative reserved
spend would exceed --cap-eur (default EUR 3.00, per docs/PHASE2_RUNBOOK.md),
the script refuses to proceed unless --i-authorize-overage is passed.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import cycle
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.budget_guard import BudgetCapExceeded, Ledger, DEFAULT_CAP_EUR
from engine.prompt_engine import GenerationRequest, build_prompt
from engine.prompt_engine.schema import IdentityPack

DEFAULT_STYLES = ["iphone_selfie", "professional_campaign", "mirror_selfie"]

# fal-ai/flux/schnell: $0.003 / megapixel, billed rounded up to the nearest
# megapixel (fal.ai pricing docs, verified 2026-08). We request an explicit
# 768x1024 (0.786 MP) rather than a size-preset string so this estimate is
# exact, not a guess at what a preset resolves to. Cost is tracked as EUR
# 1:1 with USD as a deliberately conservative simplification (real EUR cost
# is typically lower — see engine/budget_guard.py) so the cap never triggers
# later than it should.
IMAGE_WIDTH = 768
IMAGE_HEIGHT = 1024
BILLED_MEGAPIXELS_PER_IMAGE = 1  # ceil(768*1024 / 1_000_000) = ceil(0.786) = 1
FLUX_SCHNELL_PRICE_PER_MEGAPIXEL_EUR = 0.003
FLUX_SCHNELL_PRICE_PER_IMAGE = round(BILLED_MEGAPIXELS_PER_IMAGE * FLUX_SCHNELL_PRICE_PER_MEGAPIXEL_EUR, 4)


def build_candidate_requests(
    identity: IdentityPack, styles: list[str], count: int, seed_start: int = 0
) -> list[tuple[int, GenerationRequest]]:
    """Pure function: cycles through styles, assigns incrementing seeds.

    No location/outfit/pose set deliberately — this sweep is about the FACE,
    not the scene; keeping scene params minimal maximizes face-shape variety
    per image instead of spending prompt "attention" on setting.
    """
    if count < 1:
        raise ValueError("count must be >= 1")
    style_cycle = cycle(styles)
    requests = []
    for i in range(count):
        style = next(style_cycle)
        request = GenerationRequest(
            identity=identity,
            scene="portrait, looking at camera",
            photo_style=style,
        )
        requests.append((seed_start + i, request))
    return requests


def estimate_cost(count: int, price_per_image: float = FLUX_SCHNELL_PRICE_PER_IMAGE) -> float:
    return round(count * price_per_image, 4)


def generate_and_save(
    requests: list[tuple[int, GenerationRequest]],
    api_key: str,
    out_dir: Path,
    ledger: Ledger,
    cap_eur: float = DEFAULT_CAP_EUR,
    authorize_overage: bool = False,
) -> list[dict]:
    """Network I/O — requires the 'generation' extra (fal-client) and a real API key.

    Reserves each image's cost against `ledger` BEFORE calling fal.ai — if
    the reservation would exceed the cap, generation stops immediately
    (images already saved in this call remain saved; the rest are skipped).
    """
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
    results = []

    for seed, request in requests:
        ledger.reserve(FLUX_SCHNELL_PRICE_PER_IMAGE, cap_eur=cap_eur, authorize_overage=authorize_overage)

        bundle = build_prompt(request)
        handle = fal_client.submit(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": bundle.positive_prompt,
                "seed": seed,
                "image_size": {"width": IMAGE_WIDTH, "height": IMAGE_HEIGHT},
                "num_images": 1,
            },
        )
        result = handle.get()
        image_url = result["images"][0]["url"]

        image_path = out_dir / f"candidate_{seed:03d}.png"
        urllib.request.urlretrieve(image_url, image_path)

        metadata = {
            "seed": seed,
            "photo_style": request.photo_style,
            "prompt": bundle.positive_prompt,
            "negative_prompt": bundle.negative_prompt,
            "image_path": str(image_path),
            "estimated_cost_eur": FLUX_SCHNELL_PRICE_PER_IMAGE,
        }
        (out_dir / f"candidate_{seed:03d}.json").write_text(json.dumps(metadata, indent=2))
        results.append(metadata)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--identity", required=True, type=Path, help="Path to identity_pack.yaml")
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--styles", default=",".join(DEFAULT_STYLES))
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument(
        "--dry-run", action="store_true", help="Build requests and print cost estimate, no network calls"
    )
    parser.add_argument("--cap-eur", type=float, default=DEFAULT_CAP_EUR, help="Hard spend cap for the 'tier1' ledger label")
    parser.add_argument(
        "--i-authorize-overage",
        action="store_true",
        help="Explicit owner authorization to exceed --cap-eur. Do not pass this by default.",
    )
    args = parser.parse_args()

    identity = IdentityPack.from_yaml(args.identity)
    styles = [s.strip() for s in args.styles.split(",") if s.strip()]
    requests = build_candidate_requests(identity, styles, args.count, args.seed_start)

    cost = estimate_cost(args.count)
    print(f"Identity: {identity.codename} | candidates: {args.count} | estimated cost: EUR {cost}")

    if args.dry_run:
        for seed, request in requests[:3]:
            print(f"  seed={seed} style={request.photo_style} -> {build_prompt(request).positive_prompt[:100]}...")
        print(f"  ... ({len(requests)} total requests built, dry-run, no images generated)")
        return

    import os

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        print("ERROR: FAL_KEY not set. Copy .env.example to .env and fill it in.", file=sys.stderr)
        print("See docs/PHASE2_RUNBOOK.md step 1.", file=sys.stderr)
        sys.exit(1)

    out_dir = args.out_dir or (
        Path("influencers") / identity.codename.lower() / "versions" / "v1" / "candidates"
    )
    ledger = Ledger(path=out_dir.parent / ".spend_ledger.json", label="tier1")

    try:
        results = generate_and_save(
            requests, api_key, out_dir, ledger, cap_eur=args.cap_eur, authorize_overage=args.i_authorize_overage
        )
    except BudgetCapExceeded as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Saved {len(results)} candidates to {out_dir} (tier1 ledger total: EUR {ledger.spent():.2f})")


if __name__ == "__main__":
    main()
