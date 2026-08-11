from engine.prompt_engine import GenerationRequest, IdentityPack, build_prompt
from engine.prompt_engine.modules import NEGATIVE_FRAGMENT, REALISM_FRAGMENT


def _sample_identity() -> IdentityPack:
    return IdentityPack(
        codename="TEST_01",
        descriptor_fragments=["almond-shaped hazel eyes", "soft jawline"],
        body_frame="athletic, natural muscle tone",
        trigger_token="tst01woman",
        lora_path="influencers/TEST_01/versions/v1/lora/tst01_v1.safetensors",
        pulid_reference_image="influencers/TEST_01/versions/v1/canonical_refs/canonical_front.png",
        pulid_weight=0.6,
        hair_color="dark brown",
        hair_length="long",
        hair_usual_style="loose waves",
        makeup_usual="natural everyday makeup",
        signature_accessories=["thin gold hoop earrings"],
        raw={"variable_defaults": {"wardrobe_palette": ["black", "white"]}},
    )


def test_build_prompt_includes_identity_and_trigger_token():
    request = GenerationRequest(identity=_sample_identity(), scene="morning coffee", photo_style="iphone_selfie")
    bundle = build_prompt(request)

    assert "tst01woman" in bundle.positive_prompt
    assert "almond-shaped hazel eyes" in bundle.positive_prompt
    assert bundle.lora_trigger_token == "tst01woman"
    assert bundle.lora_path == request.identity.lora_path


def test_build_prompt_uses_wardrobe_default_when_outfit_not_given():
    request = GenerationRequest(identity=_sample_identity(), scene="gym session", photo_style="gym_photo")
    bundle = build_prompt(request)

    assert "usual style" in bundle.positive_prompt
    assert "black, white tones" in bundle.positive_prompt


def test_build_prompt_uses_explicit_outfit_when_given():
    request = GenerationRequest(
        identity=_sample_identity(), scene="evening out", outfit="fitted red evening dress", photo_style="nightlife"
    )
    bundle = build_prompt(request)

    assert "fitted red evening dress" in bundle.positive_prompt


def test_build_prompt_includes_location_descriptors():
    request = GenerationRequest(identity=_sample_identity(), scene="walking", location="barcelona", photo_style="travel")
    bundle = build_prompt(request)

    assert "Mediterranean" in bundle.positive_prompt


def test_build_prompt_omits_location_when_not_given():
    request = GenerationRequest(identity=_sample_identity(), scene="at home", photo_style="home_morning")
    bundle = build_prompt(request)

    assert bundle.metadata["location"] is None


def test_negative_prompt_matches_qa_checklist_intent():
    request = GenerationRequest(identity=_sample_identity(), scene="selfie", photo_style="iphone_selfie")
    bundle = build_prompt(request)

    assert NEGATIVE_FRAGMENT in bundle.negative_prompt
    assert "extra fingers" in bundle.negative_prompt


def test_extra_negative_is_appended():
    request = GenerationRequest(
        identity=_sample_identity(), scene="selfie", photo_style="iphone_selfie", extra_negative=["sunglasses"]
    )
    bundle = build_prompt(request)

    assert bundle.negative_prompt.endswith("sunglasses")


def test_realism_fragment_always_present():
    request = GenerationRequest(identity=_sample_identity(), scene="selfie", photo_style="iphone_selfie")
    bundle = build_prompt(request)

    assert REALISM_FRAGMENT in bundle.positive_prompt


def test_unknown_style_raises_helpful_error():
    request = GenerationRequest(identity=_sample_identity(), scene="selfie", photo_style="not_a_real_style")
    try:
        build_prompt(request)
        assert False, "expected KeyError"
    except KeyError as exc:
        assert "iphone_selfie" in str(exc)


def test_unknown_location_raises_helpful_error():
    request = GenerationRequest(identity=_sample_identity(), scene="selfie", photo_style="travel", location="atlantis")
    try:
        build_prompt(request)
        assert False, "expected KeyError"
    except KeyError as exc:
        assert "barcelona" in str(exc)


def test_prompt_bundle_is_deterministic():
    request = GenerationRequest(identity=_sample_identity(), scene="gym session", photo_style="gym_photo")
    first = build_prompt(request)
    second = build_prompt(request)

    assert first.positive_prompt == second.positive_prompt
    assert first.negative_prompt == second.negative_prompt
