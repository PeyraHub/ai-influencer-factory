# Experiment Log

Every training run and every meaningful generation experiment gets an entry
here — the point is to never re-pay for a configuration we already know
fails. Add a row (or a dated subsection for training runs with more detail)
per experiment. Do not delete failed experiments — they're as valuable as
successful ones.

## Format

```
### YYYY-MM-DD — <short title>
- Influencer / version:
- Type: [zero-shot exploration | dataset generation | LoRA training | production batch]
- Config: model, LoRA rank/alpha/steps (if training), prompt/seed (if generation)
- Result: what happened, Identity Consistency Score if applicable
- Cost: € and compute time
- Verdict: keep / discard / iterate — and why
```

## Log

_No experiments yet — Phase 0 spent no compute budget. First entry lands in
Phase 2 (zero-shot canonical face exploration)._
