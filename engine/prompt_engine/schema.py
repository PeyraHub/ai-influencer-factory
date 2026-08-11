"""Data structures for the modular prompt engine.

Kept deliberately dependency-light (stdlib + PyYAML only) so this can be
unit-tested without any GPU or network access. See CONTENT_PIPELINE.md §1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class IdentityPack:
    """Loaded view of an influencer's identity_pack.yaml.

    Only the fields the prompt engine actually consumes are surfaced here;
    the rest of the YAML (backstory, provenance, etc.) is kept in `raw` for
    anything downstream that needs it.
    """

    codename: str
    descriptor_fragments: list[str]
    body_frame: str
    trigger_token: str
    lora_path: str
    pulid_reference_image: str
    pulid_weight: float
    hair_color: str
    hair_length: str
    hair_usual_style: str
    makeup_usual: str
    signature_accessories: list[str]
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "IdentityPack":
        data = yaml.safe_load(Path(path).read_text())
        immutable = data.get("immutable", {}) or {}
        body = data.get("body", {}) or {}
        variable = data.get("variable_defaults", {}) or {}
        hair = variable.get("hair", {}) or {}
        conditioning = data.get("generation_conditioning", {}) or {}

        return cls(
            codename=data.get("codename", ""),
            descriptor_fragments=list(immutable.get("descriptor_fragments") or []),
            body_frame=body.get("frame", ""),
            trigger_token=conditioning.get("trigger_token", ""),
            lora_path=conditioning.get("lora_path", ""),
            pulid_reference_image=conditioning.get("pulid_reference_image", ""),
            pulid_weight=float(conditioning.get("pulid_weight", 0.6)),
            hair_color=hair.get("color", ""),
            hair_length=hair.get("length", ""),
            hair_usual_style=hair.get("usual_style", ""),
            makeup_usual=variable.get("makeup_usual", ""),
            signature_accessories=list(variable.get("signature_accessories") or []),
            raw=data,
        )


@dataclass
class GenerationRequest:
    """Everything needed to build one prompt bundle.

    Only `identity` is required — every other field falls back to the
    identity pack's variable defaults or a sensible empty value, matching
    the "usual look unless overridden" rule in IDENTITY_SYSTEM.md §1.
    """

    identity: IdentityPack
    scene: str = ""
    activity: str = ""
    mood: str = ""
    outfit: str | None = None          # None -> use identity's variable defaults
    pose: str = ""
    pose_reference_image: str | None = None  # ControlNet source, pose/composition only
    photo_style: str = "iphone_selfie"       # key into engine/styles/photo_styles.yaml
    location: str | None = None              # key into engine/locations/locations.yaml
    extra_negative: list[str] = field(default_factory=list)


@dataclass
class PromptBundle:
    """Final output of the prompt engine — everything the generation backend needs."""

    positive_prompt: str
    negative_prompt: str
    lora_path: str
    lora_trigger_token: str
    pulid_reference_image: str
    pulid_weight: float
    controlnet_reference_image: str | None
    metadata: dict[str, Any]
