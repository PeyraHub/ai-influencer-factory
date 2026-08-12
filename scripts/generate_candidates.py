#!/usr/bin/env python3
"""Phase 2, step 2 — wide zero-shot candidate face sweep.

See docs/PHASE2_RUNBOOK.md for the full procedure this script is one step
of. No identity conditioning here on purpose: there is no reference face yet
to condition on, so this is plain text-to-image from the Identity Pack's
descriptor_fragments, varied across style/seed for real diversity.

Usage:
    pip install -e ".[generation]"   # adds fal-client, only needed for this script
    cp .env.example .env             # fill in FAL_API_KEY
    python scripts/generate_candidates.py \
        --identity influencers/sofia_01/identity_pack.yaml --count 40

The request-building logic (build_candidate_requests, estimate_cost) is pure
and unit-tested without network access — see tests/test_generate_candidates.py.
Only the actual fal.ai call requires the optional 'generation' extra and a
funded account.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from itertools import cycle
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.prompt_engine import GenerationRequest, build_prompt
from engine.prompt_engine.schema import IdentityPack

DEFAULT_STYLES = ["iphone_selfie", "professional_campaign", "mirror_selfie"]
FLUX_SCHNELL_PRICE_PER_IMAGE = 0.02  # EUR, conservative estimate — see COSTS.md


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
    return round(count * price_per_image, 2)


def generate_and_save(
    requests: list[tuple[int, GenerationRequest]], api_key: str, out_dir: Path
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
    results = []

    for seed, request in requests:
        bundle = build_prompt(request)
        handle = fal_client.submit(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": bundle.positive_prompt,
                "seed": seed,
                "image_size": "portrait_4_3",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", required=True, type=Path, help="Path to identity_pack.yaml")
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--styles", default=",".join(DEFAULT_STYLES))
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument(
        "--dry-run", action="store_true", help="Build requests and print cost estimate, no network calls"
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
    api_key = os.environ.get("FAL_API_KEY")
    if not api_key:
        print("ERROR: FAL_API_KEY not set. Copy .env.example to .env and fill it in.", file=sys.stderr)
        print("See docs/PHASE2_RUNBOOK.md step 1.", file=sys.stderr)
        sys.exit(1)

    out_dir = args.out_dir or (
        Path("influencers") / identity.codename.lower() / "versions" / "v1" / "candidates"
    )
    results = generate_and_save(requests, api_key, out_dir)
    print(f"Saved {len(results)} candidates to {out_dir}")


if __name__ == "__main__":
    main()
