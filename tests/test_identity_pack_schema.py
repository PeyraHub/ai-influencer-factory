from pathlib import Path

from engine.prompt_engine.schema import IdentityPack

TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "influencers" / "_template" / "identity_pack.yaml"


def test_template_loads_even_when_mostly_blank():
    # The template ships with empty placeholder fields — from_yaml must not
    # choke on that, since Phase 1 fills it in incrementally, not atomically.
    pack = IdentityPack.from_yaml(TEMPLATE_PATH)

    assert pack.descriptor_fragments == []
    assert pack.signature_accessories == []
    assert pack.pulid_weight == 0.6


def test_from_yaml_reads_filled_fields(tmp_path):
    filled = tmp_path / "identity_pack.yaml"
    filled.write_text(
        """
codename: "TEST_02"
immutable:
  descriptor_fragments: ["warm brown eyes", "defined cheekbones"]
body:
  frame: "athletic, natural muscle tone"
variable_defaults:
  hair:
    color: "chestnut brown"
    length: "long"
    usual_style: "loose waves"
  makeup_usual: "natural everyday makeup"
  signature_accessories: ["small gold necklace"]
generation_conditioning:
  trigger_token: "tst02woman"
  lora_path: "influencers/TEST_02/versions/v1/lora/tst02_v1.safetensors"
  pulid_reference_image: "influencers/TEST_02/versions/v1/canonical_refs/canonical_front.png"
  pulid_weight: 0.55
"""
    )

    pack = IdentityPack.from_yaml(filled)

    assert pack.codename == "TEST_02"
    assert pack.descriptor_fragments == ["warm brown eyes", "defined cheekbones"]
    assert pack.trigger_token == "tst02woman"
    assert pack.pulid_weight == 0.55
    assert pack.signature_accessories == ["small gold necklace"]
