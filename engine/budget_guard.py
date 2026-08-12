"""Hard spend-cap enforcement for external paid API calls (fal.ai, etc).

Reserves a conservative cost estimate BEFORE a network call is made, against
a small persistent per-influencer-version ledger, and refuses to proceed
once cumulative reserved spend would cross a cap. This protects against
runaway spend from a larger-than-intended batch or a bug — not against
fal.ai's own billing being wrong, which this can't see.

Cost estimates are deliberately conservative (treat USD as EUR 1:1 — EUR has
historically been the stronger currency, so this only ever overestimates,
never underestimates, real EUR cost — see scripts/generate_candidates.py and
scripts/generate_variations.py for the actual per-image estimates). The cap
itself is a policy value the owner sets (CLAUDE.md §3.2, docs/PHASE2_RUNBOOK.md);
crossing it requires an explicit, deliberate override, not a default.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CAP_EUR = 3.0


class BudgetCapExceeded(RuntimeError):
    pass


@dataclass
class Ledger:
    """A tiny JSON file tracking cumulative reserved spend per label
    (e.g. "tier1") within one influencer version's directory."""

    path: Path
    label: str

    def _read(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {}

    def spent(self) -> float:
        return self._read().get(self.label, 0.0)

    def reserve(self, amount_eur: float, cap_eur: float = DEFAULT_CAP_EUR, authorize_overage: bool = False) -> float:
        """Records amount_eur against the ledger and returns the new cumulative
        total — UNLESS that would exceed cap_eur, in which case it raises
        BudgetCapExceeded and records nothing, so a rejected call can be
        retried after a real decision instead of silently drifting over cap.
        """
        if amount_eur < 0:
            raise ValueError("amount_eur must be >= 0")

        data = self._read()
        current = data.get(self.label, 0.0)
        new_total = current + amount_eur

        if new_total > cap_eur and not authorize_overage:
            raise BudgetCapExceeded(
                f"'{self.label}' spend cap: reserving EUR {amount_eur:.2f} would bring cumulative "
                f"spend to EUR {new_total:.2f}, over the EUR {cap_eur:.2f} cap (current: EUR {current:.2f}). "
                "Re-run with --i-authorize-overage only after explicit owner approval — this cap exists "
                "specifically so that never happens silently."
            )

        data[self.label] = new_total
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2))
        return new_total
