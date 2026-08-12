# Architecture

Status: **Phase 0 decisions, locked for Stage 1 (€0–30/mo).** Every decision
below is reversible except where flagged 🔒. Research backing this is in
`docs/research/stack_research_2026.md`.

## 1. System shape

```
                         ┌─────────────────────────────────────────┐
                         │            MacBook Pro 16GB              │
                         │  (orchestration, never the bottleneck)   │
                         │                                            │
   identity_pack.yaml ──▶│  Prompt Engine  ──▶  prompt bundle        │
   personality_bible ──▶│  (engine/prompt_engine)                    │
                         │                                            │
                         │  Dataset curation + scoring (local CPU)    │
                         │  InsightFace embeddings (CPU/ONNX, ~300MB) │
                         │  AI-Artifact QA heuristics (blur/res/etc.) │
                         │  Local FLUX-Schnell/klein previews (MLX/   │
                         │  MFLUX, quantized) for fast prompt         │
                         │  iteration ONLY — never final output       │
                         └───────────────┬────────────────────────────┘
                                         │ prompt bundle + control refs
                                         ▼
                         ┌─────────────────────────────────────────┐
                         │        Cloud GPU (rented by the minute)   │
                         │                                            │
                         │  LoRA training (ai-toolkit / fluxgym on   │
                         │  RunPod RTX4090/A6000 pod, spun up only    │
                         │  for training runs, then destroyed)        │
                         │                                            │
                         │  Production inference: FLUX.1-dev +        │
                         │  identity conditioning (zero-shot first,   │
                         │  LoRA only if needed — §2.2) + ControlNet  │
                         │  (RunPod pod for batches, or fal.ai/       │
                         │  Replicate serverless for one-offs —       │
                         │  zero idle cost)                            │
                         └───────────────┬────────────────────────────┘
                                         │ generated images
                                         ▼
                         ┌─────────────────────────────────────────┐
                         │            MacBook Pro 16GB               │
                         │  Face-similarity scoring vs canonical ref  │
                         │  AI-Artifact QA re-check                   │
                         │  Upscale (Real-ESRGAN, CPU/MPS, light)     │
                         │  Approve/reject → content/ + metadata      │
                         └─────────────────────────────────────────┘
```

**Rule of thumb:** anything that only touches text, YAML, small embeddings,
or a handful of images runs locally for free. Anything that needs a full
diffusion model at production resolution rents a GPU for minutes, not hours,
and nothing cloud-side stays on when idle.

## 2. Decisions

### 2.1 Base image generation model

| | |
|---|---|
| **Elegido** | FLUX.1 [dev] for production generation (cloud); FLUX.1 Schnell / FLUX.2 klein (quantized GGUF/fp8, ~7–13GB) locally for fast preview iteration only |
| **Por qué** | FLUX's transformer architecture (vs. SDXL's older UNet) currently gives the best prompt adherence, hands/anatomy, and skin texture realism of any open-weights model — directly serves priority #1 (hyperrealism) and #12 (AI-artifact removal). Schnell/klein are distilled variants small enough to fit the 16GB Mac for cheap local iteration, so we're not paying cloud GPU time to tweak wording. |
| **Alternativas descartadas** | SDXL/Pony/Illustrious ecosystem — more mature LoRA/ControlNet tooling and cheaper, but visibly behind FLUX on skin realism and hands as of 2026; kept as a fallback if FLUX LoRA training proves unstable. Midjourney/other closed APIs — no reliable per-image identity conditioning (no LoRA/IP-Adapter access), disqualifying for our core requirement. |
| **Coste aprox.** | FLUX-dev inference: cloud pod amortized ≈ €0.01–0.03/image at batch; FLUX-Schnell/klein local: €0 (electricity only) |
| **Impacto en identidad** | High — FLUX responds well to LoRA + PuLID conditioning stacked together, which is the core of our identity strategy (§2.2) |
| **Impacto en Mac** | Low — dev variant never runs locally; klein/Schnell run locally at reduced res for previews only |

### 2.2 Identity consistency method 🔒 (core decision) — progressive, measured, not presumed

| | |
|---|---|
| **Elegido** | **Progressive Identity Complexity Ladder** (full spec: `IDENTITY_SYSTEM.md` §2a). Tier 1: zero-shot identity conditioning (PuLID-Flux-II or current best equivalent) on the single canonical reference, no training — tried first, always. Tier 2: FLUX LoRA (rank 16–32) trained per-influencer, only if Tier 1's measured Identity Consistency Score is below 80/100. Tier 3: LoRA + zero-shot conditioning stacked (the original hybrid default), only if Tier 2 alone still isn't enough. |
| **Por qué** | Originally this document presumed the LoRA+PuLID hybrid as the default from the start, reasoning by trade-off analysis alone. That's backwards: it commits to a dataset-build-and-training-run cost before confirming a cheaper method doesn't already clear the bar. Research shows PuLID/InstantID-class adapters can drift under heavy lighting/pose changes for *some* identities but not necessarily all — whether Sofía's specific canonical face needs LoRA-level reinforcement is an empirical question the 15-shot Consistency Test answers directly and cheaply (§IDENTITY_SYSTEM.md §6), not something to assume upfront. Escalating only when measured avoids paying LoRA's training cost when it wouldn't have changed the outcome. |
| **Alternativas descartadas** | Committing to LoRA+PuLID hybrid as the fixed default (this doc's original position) — rejected as premature optimization; textual-inversion/embeddings alone — too weak for facial geometry, not worth testing as a tier; DreamBooth full fine-tune — far more GPU-expensive than LoRA with no accuracy benefit that justifies skipping straight past Tier 1/2; assuming Tier 1 will always be insufficient — rejected, that's exactly the assumption this ladder exists to test rather than presume. |
| **Coste aprox.** | Tier 1 only: ~€1–3 (candidate sweep + full Consistency Test, no training). Tier 2 (if needed): + ~€2–4 dataset generation + €0.20–1.50 training run. Escalation is the exception path, not the budget baseline. |
| **Impacto en identidad** | This *is* the identity system — but which tier ends up being "the identity system" for Sofía is now a measured outcome, documented in `experiments/EXPERIMENT_LOG.md`, not a fixed architectural commitment. |
| **Impacto en Mac** | Zero at every tier — zero-shot inference, training (if reached), and stacking all run cloud-side. Mac only holds the resulting reference image and (if Tier 2 is reached) LoRA file for reference/versioning. |

### 2.3 Pose, composition & scene control

| | |
|---|---|
| **Elegido** | ControlNet (OpenPose skeleton + depth map) extracted from a reference photo, applied at generation time; the reference image is converted to skeleton/depth *before* it ever reaches the identity model, so no facial information from the reference can leak into the output |
| **Por qué** | This is the standard, well-tested way to separate "what pose/composition/camera angle" (from the reference) from "who is in the photo" (from our LoRA+PuLID identity stack) — directly implements requirement §15 (reference gives pose/composition/style, never identity). |
| **Alternativas descartadas** | Raw image-to-image on the reference (img2img) — leaks too much of the reference person's face/proportions into the result, unacceptable given our no-likeness-copying rule; segmentation-only control — good for background/composition but discards useful pose detail depth+pose captures. |
| **Coste aprox.** | Included in generation cost; skeleton/depth extraction runs locally on the Mac (CPU, seconds/image) before upload |
| **Impacto en identidad** | Protective — this is what prevents "identity bleed" from reference photos |
| **Impacto en Mac** | Negligible — extraction only, not generation |

### 2.4 Cloud GPU provider

| | |
|---|---|
| **Elegido** | **RunPod** on-demand community pods (RTX 4090 ≈ €0.32/hr or A6000 ≈ €0.33/hr) for training + batch production runs; **fal.ai or Replicate** serverless (pay per image, no idle cost) for early validation and low-volume one-offs before Stage 2 |
| **Por qué** | RunPod gives the cheapest €/GPU-hour for sustained batch work with full ComfyUI/training control; serverless APIs remove all setup/idle-cost risk while we're still validating the character (Phase 1–3), at a higher per-image price that's irrelevant at low volume. Using both, sequenced by phase, keeps Stage 1 spend near €0 until there's a proven reason to spend it. |
| **Alternativas descartadas** | Thunder Compute / Lambda / Vast.ai — comparable or cheaper per-hour in some configs but less mature ComfyUI tooling and templates than RunPod; committing to a monthly reserved GPU anywhere — fixed cost we don't need at Stage 1. |
| **Coste aprox.** | See `COSTS.md` — Stage 1 target: <€10/mo total cloud GPU spend |
| **Impacto en identidad** | Neutral — same models, just where they run |
| **Impacto en Mac** | Zero load |
| **Nota** | 🔒 Creating a RunPod/fal.ai account and attaching a payment method is an external-account + money decision — flagged to you, not decided unilaterally. Grouped question at the end of this response. |

### 2.5 Local tooling (Mac 16GB)

| | |
|---|---|
| **Elegido** | Python 3.11 scripts/CLI (no heavyweight framework), PyYAML for config, InsightFace (buffalo_l, ONNX-CPU, ~300MB) for face-embedding similarity, OpenCV/Pillow for QA heuristics (blur/sharpness/resolution), MLX or MFLUX for optional local FLUX-Schnell/klein previews, Real-ESRGAN (light weights) for upscaling |
| **Por qué** | Every one of these runs comfortably in a few GB of RAM, none requires a persistent daemon, all are swappable later. This is the "orchestration and QA brain" — it never needs to hold a full FLUX-dev model in memory. |
| **Alternativas descartadas** | ComfyUI as the primary local generation engine — viable for prompt-experimentation but not required for Phase 0; ruled in later only if local preview generation earns its keep. Local LoRA training — technically possible on Apple Silicon via MLX but far slower and less mature tooling than cloud CUDA training; not worth the wall-clock time. |
| **Coste aprox.** | €0 (compute already owned) |
| **Impacto en identidad** | Indirect — this is where consistency is *measured*, not created |
| **Impacto en Mac** | Low — largest model in this list is ~300MB, runs on CPU |

### 2.6 Zero-shot candidate generation (Phase 2) — and potentially Tier 1's permanent method (§2.2)

| | |
|---|---|
| **Elegido** | Plain FLUX-schnell text-to-image (no identity conditioning — there's no reference yet) to generate and compare dozens of candidate faces cheaply; once one is chosen, PuLID-Flux-II (or current best equivalent) conditions on it for controlled variations and the Consistency Test. **This is no longer scoped to "exploration only"** — if it clears the 80/100 gate, it stays the production identity method (§2.2 Tier 1), not just a stepping stone to training. |
| **Por qué** | Generating a wide, cheap candidate pool before committing avoids wasting the (possibly unnecessary) LoRA training step on a face that doesn't survive first contact with variety. Whether zero-shot conditioning alone is *also* sufficient for production is exactly what the Consistency Test measures immediately after — no separate decision needed. |
| **Coste aprox.** | €0.01–0.04/image via fal.ai serverless, no pod rental needed, at every stage this method is used (exploration or production) |
| **Impacto en identidad** | This is how the canonical identity gets chosen, and — if it clears the gate — how it stays generated in production, with zero training cost |
| **Impacto en Mac** | Zero |

### 2.7 Data & metadata storage

| | |
|---|---|
| **Elegido** | Flat filesystem under `influencers/<codename>/versions/vN/` for images/weights (gitignored, never committed), SQLite (single file) for post/metrics/version metadata, plain YAML for identity/personality/style configs (committed to git — text only, no binaries) |
| **Por qué** | Zero infra to run, zero monthly cost, trivially backed up, and honest about current scale (one influencer, Phase 0). A database server or object-store bucket buys nothing yet. |
| **Alternativas descartadas** | Postgres — no concurrency need yet; S3/R2 bucket — deferred to Stage 2+ once local disk backup isn't enough (see `COSTS.md` for the trigger condition) |
| **Coste aprox.** | €0 |
| **Impacto en Mac** | Negligible |

## 3. What Phase 0 deliberately does NOT build yet

- No dashboard/UI (§32 of the brief — explicitly deferred until the pipeline is proven)
- No publishing automation / social API integration (Phase 9)
- No video pipeline (Phase 11)
- No multi-influencer abstraction beyond the `influencers/<codename>/` folder convention already being multi-influencer-shaped (Phase 12 just adds more folders)
- No virtual try-on / garment model (Phase 6, evaluated then — text+IP-Adapter garment conditioning is enough for Phase 1–5)

## 4. Risks

| Risk | Mitigation |
|---|---|
| LoRA-trained identity drifts across very different poses/lighting (the exact failure mode we're trying to avoid) | Formal Identity Consistency Score gate (`IDENTITY_SYSTEM.md`) before any character is declared "done"; if score is below threshold, iterate dataset/training before producing content |
| FLUX/PuLID/ComfyUI ecosystem moves fast — this stack could be stale in 3–6 months | `docs/research/` snapshots are dated; re-validate stack choice at the start of each new Phase, not continuously |
| Cloud GPU costs creep past €30/mo unnoticed | Every generation/training run logged in `experiments/EXPERIMENT_LOG.md` with cost; `COSTS.md` defines the stage-gate metrics that must be checked before increasing spend |
| Platform policy risk (Fanvue/Instagram) on AI-disclosure rules | `IDENTITY_SYSTEM.md` §Ethics documents current Fanvue AI-content disclosure requirements (mandatory AI badge/labeling); re-check policies immediately before Phase 9/10 (publishing) — flagged as a check-before-automate item |
| Local Mac becomes a bottleneck if we're tempted to run FLUX-dev locally "just this once" | Hard rule: FLUX-dev never runs locally, enforced by only wiring cloud endpoints for production generation in `engine/` |
