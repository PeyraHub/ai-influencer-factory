"""Regression test for the real Sofía (SOFIA_01) Identity Pack.

Catches schema drift between influencers/sofia_01/identity_pack.yaml and
engine/prompt_engine/schema.py, and sanity-checks the immutable/variable
separation actually holds for a real production identity, not just the
synthetic fixture used in test_prompt_engine.py.
"""
from pathlib import Path

from engine.prompt_engine import GenerationRequest, build_prompt
from engine.prompt_engine.schema import IdentityPack

SOFIA_PATH = Path(__file__).resolve().parents[1] / "influencers" / "sofia_01" / "identity_pack.yaml"


def test_sofia_identity_pack_loads():
    pack = IdentityPack.from_yaml(SOFIA_PATH)

    assert pack.codename == "SOFIA_01"
    assert pack.trigger_token == "sofia01woman"
    assert len(pack.descriptor_fragments) >= 5


def test_sofia_immutable_traits_not_duplicated_in_variable_defaults():
    # Eye color / freckles / body frame are IMMUTABLE (IDENTITY_SYSTEM.md §1)
    # and must live only in the immutable/body blocks, never re-declared as
    # if they were styling choices.
    pack = IdentityPack.from_yaml(SOFIA_PATH)
    raw = pack.raw

    variable_defaults = raw.get("variable_defaults", {})
    assert "eyes" not in variable_defaults
    assert "freckles" not in str(variable_defaults).lower()
    assert "hazel" not in str(variable_defaults).lower()

    # Hair, by contrast, IS variable per IDENTITY_SYSTEM.md §1 even though
    # Sofía has a signature color — it must live under variable_defaults, not immutable.
    assert "hair" not in raw.get("immutable", {})
    assert variable_defaults.get("hair", {}).get("color", "").startswith("deep mahogany")


def test_sofia_body_frame_matches_fitness_natural_decision():
    pack = IdentityPack.from_yaml(SOFIA_PATH)
    assert "toned" in pack.body_frame.lower() or "athletic" in pack.body_frame.lower()
    assert "not hypersexualized" in pack.raw["body"]["explicit_non_goals"]


def test_build_prompt_end_to_end_with_sofia():
    pack = IdentityPack.from_yaml(SOFIA_PATH)
    request = GenerationRequest(
        identity=pack, scene="morning run along the beach", photo_style="iphone_selfie", location="barcelona"
    )
    bundle = build_prompt(request)

    assert "sofia01woman" in bundle.positive_prompt
    assert "honey hazel eyes" in bundle.positive_prompt
    assert "Mediterranean" in bundle.positive_prompt
    assert bundle.lora_trigger_token == "sofia01woman"
