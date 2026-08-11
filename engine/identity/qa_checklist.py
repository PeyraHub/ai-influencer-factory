"""AI-Artifact QA — the automatable slice, plus the manual checklist text.

See IDENTITY_SYSTEM.md §7 for the full checklist and rationale. Only two
items are cheaply automatable without a trained detector (sharpness,
resolution); everything else stays a human checklist item until Phase 7
(Automated QA) justifies building/training a detector for it — automating a
check we can't yet do reliably would be worse than a clear manual checklist.

Dependencies: Pillow + numpy only — runs fine on the Mac, no GPU needed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

# Mirrors IDENTITY_SYSTEM.md §7 verbatim so the checklist used in code review
# / manual QA sessions never drifts from the documented one.
MANUAL_ARTIFACT_CHECKLIST: list[str] = [
    "Skin texture shows natural variation (pores, minor asymmetry) — not airbrushed/plastic",
    "Eyes: catchlights consistent with scene lighting, pupils same size, no glassy/dead look",
    "Teeth: countable, natural spacing/shape, no fusion or extra teeth",
    "Hair: strands resolve individually at the edges, no clumping, flyaways where plausible",
    "Hands: 5 fingers, plausible joints, no fusion/extra digits",
    "Nails: present, plausible shape, consistent across visible hands",
    "Jewelry/earrings: symmetric where they should be, no melting into skin",
    "Clothing: seams/fabric behave physically, no melting into skin, text/logos not garbled",
    "No garbled text anywhere in frame",
    "Reflections (mirrors, windows, sunglasses) are geometrically plausible",
    "Lighting direction/color consistent across the whole frame",
    "Depth of field/perspective consistent with the stated camera/lens",
    "No excessive/uncanny symmetry in the face",
    "Background objects are coherent (no melted furniture, impossible architecture)",
    "Body proportions match the canonical body reference",
]


@dataclass
class QAResult:
    image_path: str
    sharpness: float
    resolution_ok: bool
    manual_checklist_passed: bool | None = None  # filled in by a human reviewer
    notes: str = ""

    @property
    def auto_pass(self) -> bool:
        """Automated pre-filter only — never a substitute for the manual checklist."""
        return self.resolution_ok and self.sharpness >= 50.0


def _to_grayscale_array(image_path: str | Path) -> np.ndarray:
    with Image.open(image_path) as img:
        return np.asarray(img.convert("L"), dtype=np.float64)


def sharpness_score(image_path: str | Path) -> float:
    """Variance of the discrete Laplacian — a standard, cheap blur detector.

    Higher = sharper. Rejects the "obviously soft/blurry" failure mode before
    it ever reaches a human or a face-embedding model. Not a substitute for
    the manual artifact checklist — a sharp image can still fail every other
    item on that list.
    """
    gray = _to_grayscale_array(image_path)
    # 3x3 discrete Laplacian kernel [[0,1,0],[1,-4,1],[0,1,0]] via shifted sums,
    # vectorized to avoid a scipy/opencv dependency for one small operation.
    center = gray[1:-1, 1:-1]
    up = gray[:-2, 1:-1]
    down = gray[2:, 1:-1]
    left = gray[1:-1, :-2]
    right = gray[1:-1, 2:]
    laplacian = up + down + left + right - 4 * center
    return float(laplacian.var())


def check_resolution(image_path: str | Path, min_width: int = 1024, min_height: int = 1024) -> bool:
    with Image.open(image_path) as img:
        width, height = img.size
    return width >= min_width and height >= min_height


def run_automated_qa(image_path: str | Path, min_width: int = 1024, min_height: int = 1024) -> QAResult:
    return QAResult(
        image_path=str(image_path),
        sharpness=sharpness_score(image_path),
        resolution_ok=check_resolution(image_path, min_width, min_height),
    )
