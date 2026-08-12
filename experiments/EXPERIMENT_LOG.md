# Experiment Log

Every training run and every meaningful generation/growth experiment gets an
entry here — the point is to never re-pay for a configuration we already
know fails, and to never keep running a strategy that isn't working out of
attachment (`CLAUDE.md` §7). Add a row (or a dated subsection for training
runs with more detail) per experiment. Do not delete failed experiments —
they're as valuable as successful ones.

**Define success/kill criteria BEFORE running the experiment, not after
seeing the result** — deciding the bar after you've seen the outcome is just
confirmation bias with extra steps.

## Format

```
### YYYY-MM-DD — <short title>
- Influencer / version:
- Type: [zero-shot exploration | dataset generation | LoRA training | production batch | growth experiment]
- Success criterion: [defined BEFORE running]
- Kill criterion: [defined BEFORE running]
- Config: model, LoRA rank/alpha/steps (if training), prompt/seed (if generation)
- Result: what happened, Identity Consistency Score if applicable
- Cost: € and compute time
- Verdict: keep / discard / iterate — and why, against the criteria above
```

## Log

_No experiments yet — Phase 0 spent no compute budget. First entry lands in
Phase 2 (zero-shot canonical face exploration)._
