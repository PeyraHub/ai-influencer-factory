# Cost model

## Budget stages

| Stage | Monthly budget | Unlocked when | What changes |
|---|---|---|---|
| 1 — Validation | €0–30 | Now | Serverless pay-per-image for exploration, on-demand pods only for training runs, everything else local/free |
| 2 — First sales / growth | €30–100 | First brand micro-deal or Fanvue revenue covers Stage 1 spend for 2 consecutive months | Increase generation volume, keep a training pod for longer sessions, add cloud storage backup (R2/B2 paid tier if free tier exceeded) |
| 3 — Automation & volume | €100–300 | Revenue ≥ 3× Stage 2 spend, sustained 2 months | Reserved/spot GPU block for daily batch generation, add publishing automation tooling, consider a second influencer |
| 4 — Profitable scale | €300+ | Revenue comfortably covers Stage 3 + positive margin | Dedicated GPU capacity, dashboard (Phase 32 territory), team/tooling investment |

**Rule:** never move to the next stage's spend level without the revenue
trigger above. Cost decisions are logged in `experiments/EXPERIMENT_LOG.md`
so we can see the €/output trend, not just guess at it.

## Stage 1 cost breakdown (target: <€30/mo, realistically <€10/mo)

| Item | Cost | Notes |
|---|---|---|
| Zero-shot exploration (Phase 2) | ~€1–2 one-time | ~40 candidate images via fal.ai/Replicate serverless @ €0.02–0.04/img |
| Dataset generation (Phase 3) | ~€1–2 one-time | ~30 controlled-variation images |
| LoRA training (Phase 4, per version) | €0.20–1.50 | 30–90 min on rented RTX4090/A6000 @ ~€0.32–0.35/hr |
| Production generation (Phase 6+) | €0.01–0.03/image | RunPod batch or serverless, depends on volume |
| Local tooling | €0 | Runs on hardware already owned |
| Cloud backup storage | €0 | Free tier (R2 10GB / B2 10GB) sufficient at this scale |
| **Total, first month with one influencer through Phase 6** | **≈ €5–15** | Leaves headroom under the €30 ceiling for iteration/re-training |

## Unit economics — track these, not vanity metrics

```
€ / 100 images generated        = total generation spend / (images generated / 100)
€ / image approved              = total spend / images that passed QA + identity score
€ / post published               = total spend / posts actually published
GPU-minutes / image              = pod wall-clock time / images produced in that run
acceptance rate                  = images approved / images generated
generation-to-post ratio         = images generated / images published
```

**Funnel target (from the brief's own example, treat as the working
hypothesis until real data replaces it):**
```
100 generated → ~30 technically clean → ~10 excellent → ~3 published
```
If actual acceptance rate is far below this after Phase 6, the problem is
diagnosed in `IDENTITY_SYSTEM.md` (identity/QA) before spending more on volume
— more generation is never the fix for a low acceptance rate.

## What we do NOT pay for at Stage 1

- No reserved/monthly GPU capacity
- No dashboard/SaaS tooling
- No paid scheduling/publishing tools (manual publish is fine at this volume)
- No paid stock/reference libraries
- No LLM API subscriptions beyond free/pay-per-call tiers for captioning (if
  used — evaluate against local small-model captioning first)

Every recurring paid subscription is a Stage-2+ decision and requires your
sign-off (money decision, per your standing instructions).
