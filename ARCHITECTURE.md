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
                         │  identity LoRA + PuLID-Flux-II + ControlNet│
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

### 2.2 Identity consistency method 🔒 (core decision)

| | |
|---|---|
| **Elegido** | **Hybrid: FLUX LoRA (trained per-influencer, rank 16–32) as the durable identity backbone + PuLID-Flux-II as a zero-shot identity reinforcement layer stacked on top, at moderate weight** |
| **Por qué** | Research is consistent on the trade-off: PuLID/InstantID-style adapters give instant, training-free identity lock from 1 reference photo but drift under heavy lighting/pose changes and can look "pasted on"; a trained LoRA captures identity *and* body language *and* skin/hair texture as a reusable asset, at the cost of needing a curated dataset and a training run. Stacking both (LoRA for the durable "who this is", PuLID for an extra identity anchor per-generation) is the current best-practice pattern for long-lived characters — it directly optimizes our stated equation of identity × realism × flexibility, and the LoRA becomes the actual sellable/reusable IP for the influencer. |
| **Alternativas descartadas** | PuLID/InstantID alone — faster to start (Phase 1 will actually use this, see 2.6), but insufficient for the "same person across 15+ wildly different scenes" requirement (§ IDENTITY_SYSTEM.md Consistency Test); textual-inversion/embeddings alone — too weak for facial geometry; DreamBooth full fine-tune — full-model fine-tuning is far more GPU-expensive and harder to keep flexible for outfit/pose variety than a LoRA, no accuracy benefit that justifies the cost here. |
| **Coste aprox.** | One LoRA training run ≈ 30–90 min on a rented 24GB+ GPU ≈ €0.20–1.50 per training run (§ COSTS.md). Re-trained only on version bumps (v1→v2), not per image. |
| **Impacto en identidad** | This *is* the identity system. |
| **Impacto en Mac** | Zero — training and PuLID inference both run cloud-side. Mac only holds the resulting LoRA file (tens of MB) for reference/versioning. |

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

### 2.6 Zero-shot exploration for canonical face selection (Phase 1–2 only)

| | |
|---|---|
| **Elegido** | PuLID-Flux-II (or InstantID as fallback) used stand-alone, no training, to generate and compare dozens of candidate faces cheaply before committing to one identity |
| **Por qué** | Training a LoRA on a face that doesn't survive first contact with variety would waste the one expensive step in the pipeline. Zero-shot adapters let us throw away 95% of candidates for free (serverless, pay-per-image) before any dataset/training investment. |
| **Coste aprox.** | €0.01–0.04/image via fal.ai/Replicate serverless, no pod rental needed |
| **Impacto en identidad** | This is how the canonical identity gets chosen in the first place |
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
