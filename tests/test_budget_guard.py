import pytest

from engine.budget_guard import BudgetCapExceeded, Ledger


def test_reserve_within_cap_succeeds(tmp_path):
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")
    total = ledger.reserve(1.0, cap_eur=3.0)
    assert total == 1.0
    assert ledger.spent() == 1.0


def test_reserve_accumulates_across_calls(tmp_path):
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")
    ledger.reserve(1.0, cap_eur=3.0)
    total = ledger.reserve(1.5, cap_eur=3.0)
    assert total == 2.5
    assert ledger.spent() == 2.5


def test_reserve_persists_across_ledger_instances(tmp_path):
    path = tmp_path / "ledger.json"
    Ledger(path=path, label="tier1").reserve(1.0, cap_eur=3.0)
    # A fresh Ledger instance pointed at the same file sees prior spend —
    # this is what makes the cap survive across separate script invocations
    # (e.g. the 2-image test, then the full 40-image sweep).
    second = Ledger(path=path, label="tier1")
    assert second.spent() == 1.0
    second.reserve(0.5, cap_eur=3.0)
    assert second.spent() == 1.5


def test_reserve_over_cap_raises_and_does_not_record(tmp_path):
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")
    ledger.reserve(2.5, cap_eur=3.0)
    with pytest.raises(BudgetCapExceeded):
        ledger.reserve(1.0, cap_eur=3.0)
    # The rejected reservation must not have been recorded.
    assert ledger.spent() == 2.5


def test_reserve_over_cap_with_authorization_succeeds(tmp_path):
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")
    ledger.reserve(2.5, cap_eur=3.0)
    total = ledger.reserve(1.0, cap_eur=3.0, authorize_overage=True)
    assert total == 3.5


def test_separate_labels_have_independent_budgets(tmp_path):
    path = tmp_path / "ledger.json"
    Ledger(path=path, label="tier1").reserve(2.9, cap_eur=3.0)
    # A different label (e.g. a second influencer, or Tier 2) is unaffected.
    tier2 = Ledger(path=path, label="tier2")
    assert tier2.spent() == 0.0
    tier2.reserve(2.9, cap_eur=3.0)


def test_negative_amount_rejected(tmp_path):
    ledger = Ledger(path=tmp_path / "ledger.json", label="tier1")
    with pytest.raises(ValueError):
        ledger.reserve(-1.0)
