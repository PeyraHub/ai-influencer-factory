"""Identity Consistency Score — see IDENTITY_SYSTEM.md §6 for the full spec.

    Score = 0.40 * FaceEmbeddingScore
          + 0.20 * BodyProportionScore
          + 0.20 * DistinctiveFeatureScore
          + 0.20 * HumanReviewScore

`combine_identity_score` is pure arithmetic (no heavy deps, unit-tested
without any GPU). `face_embedding_similarity` needs `insightface` +
`onnxruntime` installed — imported lazily so the rest of this module (and
the whole test suite) works without them until Phase 5 actually needs to
score real images.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PASS_THRESHOLD = 80.0

_WEIGHTS = {
    "face_embedding": 0.40,
    "body_proportion": 0.20,
    "distinctive_feature": 0.20,
    "human_review": 0.20,
}


@dataclass
class ConsistencyScoreInputs:
    """All sub-scores on a 0-100 scale — see IDENTITY_SYSTEM.md §6 for how each is derived."""

    face_embedding_score: float
    body_proportion_score: float
    distinctive_feature_score: float
    human_review_score: float


def combine_identity_score(inputs: ConsistencyScoreInputs) -> float:
    for name, value in vars(inputs).items():
        if not 0.0 <= value <= 100.0:
            raise ValueError(f"{name} must be within 0-100, got {value}")

    return (
        _WEIGHTS["face_embedding"] * inputs.face_embedding_score
        + _WEIGHTS["body_proportion"] * inputs.body_proportion_score
        + _WEIGHTS["distinctive_feature"] * inputs.distinctive_feature_score
        + _WEIGHTS["human_review"] * inputs.human_review_score
    )


def passes_gate(score: float) -> bool:
    return score >= PASS_THRESHOLD


def face_embedding_similarity(candidate_image: str | Path, canonical_reference: str | Path) -> float:
    """Cosine similarity between one candidate image and the canonical reference,
    scaled to 0-100. Requires `insightface` + `onnxruntime` (not in the core
    dependency set — see pyproject.toml `[project.optional-dependencies].identity`).
    """
    try:
        import numpy as np
        from insightface.app import FaceAnalysis
    except ImportError as exc:  # pragma: no cover - exercised only without the optional deps
        raise ImportError(
            "face_embedding_similarity requires the 'identity' extra: "
            "pip install -e '.[identity]'"
        ) from exc

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))

    def _embedding(path: str | Path) -> "np.ndarray":
        import cv2  # insightface's expected input format

        img = cv2.imread(str(path))
        if img is None:
            raise FileNotFoundError(f"Could not read image: {path}")
        faces = app.get(img)
        if not faces:
            raise ValueError(f"No face detected in: {path}")
        # Largest detected face, in case of incidental background people.
        face = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
        return face.normed_embedding

    a = _embedding(candidate_image)
    b = _embedding(canonical_reference)
    cosine_similarity = float(np.dot(a, b))
    return max(0.0, min(100.0, (cosine_similarity + 1.0) / 2.0 * 100.0))


def average_face_embedding_score(
    candidate_images: list[str | Path], canonical_reference: str | Path
) -> float:
    """FaceEmbeddingScore for the full 15-shot Consistency Test batch — the
    average similarity across all test images vs. the single canonical
    frontal reference (IDENTITY_SYSTEM.md §6)."""
    if not candidate_images:
        raise ValueError("candidate_images must not be empty")
    scores = [face_embedding_similarity(img, canonical_reference) for img in candidate_images]
    return sum(scores) / len(scores)
