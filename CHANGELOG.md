# Changelog

All notable changes to this project. Dated, reverse-chronological.

## 2026-08-11 — Phase 0: Research & Architecture

- Repo initialized from empty.
- Researched current (Aug 2026) state of: FLUX/PuLID/InstantID identity
  consistency methods, cloud GPU pricing (RunPod/fal.ai/Replicate/Thunder
  Compute), ComfyUI/FLUX LoRA training workflows, Fanvue AI-content policy,
  and Apple Silicon 16GB local generation feasibility. Sources and findings
  in `docs/research/stack_research_2026.md`.
- Wrote core documentation: `ARCHITECTURE.md`, `ROADMAP.md`, `COSTS.md`,
  `IDENTITY_SYSTEM.md`, `CONTENT_PIPELINE.md`.
- Locked stack decision: FLUX.1-dev (cloud) for production generation,
  FLUX-Schnell/klein (local, quantized) for preview iteration only; hybrid
  LoRA (durable identity) + PuLID-Flux-II (per-generation reinforcement) for
  identity consistency; ControlNet pose/depth for composition control without
  identity leakage; RunPod on-demand pods + fal.ai/Replicate serverless for
  cloud compute, billed by the minute/image, no reserved capacity.
- Scaffolded repo structure: `influencers/`, `engine/` (prompt_engine,
  identity, styles, locations), `content/`, `experiments/`, `tests/`.
- Implemented and tested (pytest, no GPU/API required):
  - `engine/prompt_engine` — modular prompt composition from Identity Pack +
    scene/outfit/pose/camera/lighting/location parameters
  - `engine/identity/qa_checklist.py` — local heuristic checks (sharpness,
    resolution) usable pre-GPU
  - `engine/identity/consistency_score.py` — Identity Consistency Score
    implementation (InsightFace-based), interface finalized, requires
    `insightface`/`onnxruntime` install to run against real images
- Added `influencers/_template/identity_pack.yaml` and
  `personality_bible.yaml` with the immutable/variable trait schema from
  `IDENTITY_SYSTEM.md`.
- No money spent. No external accounts created. No images generated yet —
  Phase 1 (identity design) starts once character creative decisions and the
  cloud-GPU-account decision are confirmed.
