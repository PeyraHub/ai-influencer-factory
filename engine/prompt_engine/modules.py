"""Modular prompt composition.

Each `_build_*` function returns one prompt fragment for one module
(BASE IDENTITY / SCENE / OUTFIT / POSE / CAMERA / LIGHTING / REALISM /
NEGATIVE / IDENTITY CONTROL — see CONTENT_PIPELINE.md §1). `build_prompt`
composes them into a `PromptBundle`. Pure functions, no I/O beyond the two
small YAML lookups for style/location — fully unit-testable without a GPU.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .schema import GenerationRequest, IdentityPack, PromptBundle

_STYLES_PATH = Path(__file__).resolve().parents[1] / "styles" / "photo_styles.yaml"
_LOCATIONS_PATH = Path(__file__).resolve().parents[1] / "locations" / "locations.yaml"

# Fixed boilerplate, tuned once and reused everywhere (ARCHITECTURE.md §2.1,
# IDENTITY_SYSTEM.md §7 — mirrors the AI-Artifact QA checklist so we steer
# away from exactly what QA checks for).
REALISM_FRAGMENT = (
    "natural skin texture with visible pores and subtle asymmetry, "
    "realistic photographic detail, authentic candid quality"
)

NEGATIVE_FRAGMENT = (
    "plastic skin, airbrushed skin, waxy skin, extra fingers, fused fingers, "
    "malformed hands, extra limbs, warped jaw, asymmetric eyes, blurry teeth, "
    "melted jewelry, garbled text, distorted logos, overly symmetric face, "
    "uncanny valley, doll-like, 3d render look, cgi look"
)


@lru_cache(maxsize=1)
def _load_styles() -> dict[str, Any]:
    return yaml.safe_load(_STYLES_PATH.read_text())


@lru_cache(maxsize=1)
def _load_locations() -> dict[str, Any]:
    return yaml.safe_load(_LOCATIONS_PATH.read_text())


def _build_base_identity(identity: IdentityPack) -> str:
    fragments = ", ".join(identity.descriptor_fragments) if identity.descriptor_fragments else ""
    parts = [identity.trigger_token, fragments, identity.body_frame]
    return ", ".join(p for p in parts if p)


def _build_scene(request: GenerationRequest) -> str:
    parts = [request.scene, request.activity, request.mood]
    return ", ".join(p for p in parts if p)


def _build_outfit(request: GenerationRequest) -> str:
    if request.outfit:
        return request.outfit
    identity = request.identity
    palette = ", ".join(identity.raw.get("variable_defaults", {}).get("wardrobe_palette", []) or [])
    return f"outfit in her usual style{f', {palette} tones' if palette else ''}"


def _build_pose(request: GenerationRequest) -> str:
    return request.pose


def _build_camera_and_lighting(request: GenerationRequest) -> tuple[str, str]:
    styles = _load_styles()
    style = styles.get(request.photo_style)
    if style is None:
        known = ", ".join(sorted(styles))
        raise KeyError(f"Unknown photo_style {request.photo_style!r}. Known styles: {known}")
    return style["camera_fragment"], style["lighting_fragment"]


def _build_location(request: GenerationRequest) -> str:
    if not request.location:
        return ""
    locations = _load_locations()
    location = locations.get(request.location)
    if location is None:
        known = ", ".join(sorted(locations))
        raise KeyError(f"Unknown location {request.location!r}. Known locations: {known}")
    return location["visual_descriptors"]


def _build_hair_and_makeup(identity: IdentityPack) -> str:
    hair = ", ".join(p for p in (identity.hair_color, identity.hair_length, identity.hair_usual_style) if p)
    parts = [hair, identity.makeup_usual]
    if identity.signature_accessories:
        parts.append(", ".join(identity.signature_accessories))
    return ", ".join(p for p in parts if p)


def build_prompt(request: GenerationRequest) -> PromptBundle:
    """Compose a full prompt bundle from a GenerationRequest.

    Deterministic and side-effect free apart from the cached style/location
    YAML lookups — same request always produces the same bundle, which is
    what makes prompts reproducible/versionable (IDENTITY_SYSTEM.md, brief §19).
    """
    identity = request.identity
    camera_fragment, lighting_fragment = _build_camera_and_lighting(request)

    positive_segments = [
        _build_base_identity(identity),
        _build_hair_and_makeup(identity),
        _build_scene(request),
        _build_outfit(request),
        _build_pose(request),
        _build_location(request),
        camera_fragment,
        lighting_fragment,
        REALISM_FRAGMENT,
    ]
    positive_prompt = ", ".join(s for s in positive_segments if s)

    negative_segments = [NEGATIVE_FRAGMENT, *request.extra_negative]
    negative_prompt = ", ".join(s for s in negative_segments if s)

    return PromptBundle(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        lora_path=identity.lora_path,
        lora_trigger_token=identity.trigger_token,
        pulid_reference_image=identity.pulid_reference_image,
        pulid_weight=identity.pulid_weight,
        controlnet_reference_image=request.pose_reference_image,
        metadata={
            "codename": identity.codename,
            "scene": request.scene,
            "activity": request.activity,
            "mood": request.mood,
            "photo_style": request.photo_style,
            "location": request.location,
        },
    )
