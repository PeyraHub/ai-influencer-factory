#!/usr/bin/env python3
"""Phase 5 — Identity Consistency Score, computed from a generated 15-shot
Character Consistency Test set (IDENTITY_SYSTEM.md §6).

Combines the automated FaceEmbeddingScore (InsightFace cosine similarity
against the canonical reference) with three manually-reviewed sub-scores
(body proportion, distinctive feature, human review — see
IDENTITY_SYSTEM.md §6, these three are deliberately NOT automated) into the
final 0-100 score, and checks it against the 80/100 gate.

Usage:
    pip install -e ".[identity]"     # adds insightface/onnxruntime, only needed for this script
    cp influencers/_template/manual_consistency_scores.yaml \
       influencers/sofia_01/versions/v1/manual_consistency_scores.yaml
    # ... fill in the three manual scores after reviewing the 15 shots ...
    python scripts/score_consistency.py \
        --shots-dir influencers/sofia_01/versions/v1/consistency_test \
        --canonical-ref influencers/sofia_01/versions/v1/canonical_refs/canonical_front.png \
        --manual-scores influencers/sofia_01/versions/v1/manual_consistency_scores.yaml \
        --tier 1
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.identity.consistency_score import (
    PASS_THRESHOLD,
    ConsistencyScoreInputs,
    combine_identity_score,
    passes_gate,
)

REQUIRED_MANUAL_KEYS = ("body_proportion_score", "distinctive_feature_score", "human_review_score")


def load_manual_scores(path: str | Path) -> dict[str, float]:
    """Pure function: loads and validates the human-filled manual scores file."""
    data = yaml.safe_load(Path(path).read_text()) or {}
    missing = [k for k in REQUIRED_MANUAL_KEYS if k not in data]
    if missing:
        raise ValueError(
            f"manual scores file is missing {missing} — fill in "
            "influencers/_template/manual_consistency_scores.yaml before running"
        )
    return {k: float(data[k]) for k in REQUIRED_MANUAL_KEYS}


def build_score_inputs(face_embedding_score: float, manual_scores: dict[str, float]) -> ConsistencyScoreInputs:
    """Pure function: assembles the four sub-scores into the scoring input."""
    return ConsistencyScoreInputs(
        face_embedding_score=face_embedding_score,
        body_proportion_score=manual_scores["body_proportion_score"],
        distinctive_feature_score=manual_scores["distinctive_feature_score"],
        human_review_score=manual_scores["human_review_score"],
    )


def format_report(score: float, inputs: ConsistencyScoreInputs, tier: int) -> str:
    verdict = "PASS" if passes_gate(score) else "FAIL"
    return f"""# Identity Consistency Report — Tier {tier}

| Sub-score | Value |
|---|---|
| FaceEmbeddingScore (40%) | {inputs.face_embedding_score:.1f} |
| BodyProportionScore (20%) | {inputs.body_proportion_score:.1f} |
| DistinctiveFeatureScore (20%) | {inputs.distinctive_feature_score:.1f} |
| HumanReviewScore (20%) | {inputs.human_review_score:.1f} |
| **Total** | **{score:.1f} / 100** |

**Threshold:** {PASS_THRESHOLD} / 100
**Verdict:** {verdict}

{"Identity locked at Tier " + str(tier) + " — proceed to Phase 6." if verdict == "PASS" else
 "Escalate to the next tier of the Progressive Identity Complexity Ladder (IDENTITY_SYSTEM.md §2a)."}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots-dir", required=True, type=Path, help="Dir of 15 images from generate_variations.py --shots all")
    parser.add_argument("--canonical-ref", required=True, type=Path)
    parser.add_argument("--manual-scores", required=True, type=Path)
    parser.add_argument("--tier", type=int, default=1, choices=[1, 2, 3])
    parser.add_argument("--out", type=Path, default=None, help="Where to write consistency_report.md")
    args = parser.parse_args()

    manual_scores = load_manual_scores(args.manual_scores)

    shot_images = sorted(p for p in args.shots_dir.glob("*.png"))
    if not shot_images:
        print(f"ERROR: no .png files found in {args.shots_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        from engine.identity.consistency_score import average_face_embedding_score
    except ImportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    face_embedding_score = average_face_embedding_score(shot_images, args.canonical_ref)
    inputs = build_score_inputs(face_embedding_score, manual_scores)
    score = combine_identity_score(inputs)

    report = format_report(score, inputs, args.tier)
    print(report)

    out_path = args.out or (args.shots_dir.parent / "consistency_report.md")
    out_path.write_text(report)
    print(f"Written to {out_path}")

    sys.exit(0 if passes_gate(score) else 1)


if __name__ == "__main__":
    main()
