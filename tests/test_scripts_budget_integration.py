"""Integration tests: the hard spend cap actually stops execution BEFORE any
network call, for both generation scripts. fal_client is mocked (it's an
optional extra, not installed in the base test environment) so these run
without network access or a real API key.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from engine.budget_guard import BudgetCapExceeded, Ledger
from engine.prompt_engine.schema import IdentityPack

SOFIA_PATH = Path(__file__).resolve().parents[1] / "influencers" / "sofia_01" / "identity_pack.yaml"


def _fake_fal_client():
    fake = MagicMock()
    fake_handle = MagicMock()
    fake_handle.get.return_value = {"images": [{"url": "https://example.com/fake.png"}]}
    fake.submit.return_value = fake_handle
    fake.upload_file.return_value = "https://example.com/uploaded.png"
    return fake


def test_generate_candidates_stops_before_network_call_over_cap(tmp_path, monkeypatch):
    from generate_candidates import build_candidate_requests, generate_and_save

    fake_fal_client = _fake_fal_client()
    monkeypatch.setitem(sys.modules, "fal_client", fake_fal_client)
    monkeypatch.setattr("urllib.request.urlretrieve", lambda url, path: Path(path).write_bytes(b"x"))

    identity = IdentityPack.from_yaml(SOFIA_PATH)
    requests = build_candidate_requests(identity, ["iphone_selfie"], count=3)
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")

    with pytest.raises(BudgetCapExceeded):
        generate_and_save(requests, "fake-key", tmp_path / "out", ledger, cap_eur=0.001)

    fake_fal_client.submit.assert_not_called()
    assert not (tmp_path / "out").exists() or not any((tmp_path / "out").iterdir())


def test_generate_candidates_authorize_overage_proceeds(tmp_path, monkeypatch):
    from generate_candidates import build_candidate_requests, generate_and_save

    fake_fal_client = _fake_fal_client()
    monkeypatch.setitem(sys.modules, "fal_client", fake_fal_client)
    monkeypatch.setattr("urllib.request.urlretrieve", lambda url, path: Path(path).write_bytes(b"x"))

    identity = IdentityPack.from_yaml(SOFIA_PATH)
    requests = build_candidate_requests(identity, ["iphone_selfie"], count=1)
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")

    results = generate_and_save(requests, "fake-key", tmp_path / "out", ledger, cap_eur=0.001, authorize_overage=True)

    assert len(results) == 1
    fake_fal_client.submit.assert_called_once()


def test_generate_variations_stops_before_network_call_over_cap(tmp_path, monkeypatch):
    from generate_variations import build_shot_requests, generate_and_save

    fake_fal_client = _fake_fal_client()
    monkeypatch.setitem(sys.modules, "fal_client", fake_fal_client)
    monkeypatch.setattr("urllib.request.urlretrieve", lambda url, path: Path(path).write_bytes(b"x"))

    identity = IdentityPack.from_yaml(SOFIA_PATH)
    requests = build_shot_requests(identity, "https://example.com/ref.png", ["selfie", "gym"])
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")

    with pytest.raises(BudgetCapExceeded):
        generate_and_save(requests, "ref.png", "fake-key", tmp_path / "out", ledger, cap_eur=0.001)

    fake_fal_client.submit.assert_not_called()


def test_candidates_and_variations_share_ledger_cumulatively(tmp_path, monkeypatch):
    # Both scripts write to the same "tier1" label — spending from the
    # candidate sweep must count against the shortlist/consistency-test cap.
    from generate_candidates import build_candidate_requests
    from generate_candidates import generate_and_save as generate_candidates_and_save
    from generate_variations import build_shot_requests
    from generate_variations import generate_and_save as generate_variations_and_save

    fake_fal_client = _fake_fal_client()
    monkeypatch.setitem(sys.modules, "fal_client", fake_fal_client)
    monkeypatch.setattr("urllib.request.urlretrieve", lambda url, path: Path(path).write_bytes(b"x"))

    identity = IdentityPack.from_yaml(SOFIA_PATH)
    ledger_path = tmp_path / "ledger.json"

    candidate_requests = build_candidate_requests(identity, ["iphone_selfie"], count=1)
    generate_candidates_and_save(
        candidate_requests, "fake-key", tmp_path / "candidates", Ledger(path=ledger_path, label="tier1"), cap_eur=3.0
    )

    variation_requests = build_shot_requests(identity, "https://example.com/ref.png", ["selfie"])
    ledger = Ledger(path=ledger_path, label="tier1")
    spent_before = ledger.spent()
    generate_variations_and_save(
        variation_requests, "ref.png", "fake-key", tmp_path / "variations", ledger, cap_eur=3.0
    )

    assert ledger.spent() > spent_before  # cumulative, not reset per script
