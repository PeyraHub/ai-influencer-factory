# Changelog

All notable changes to this project. Dated, reverse-chronological.

## 2026-08-12 — Execution mode: permanent operating rules + commercial plan + Phase 2 runbook

- Added `CLAUDE.md`: permanent, session-surviving operating rules —
  maximum autonomy, minimum interruptions, explicit stop conditions (money,
  external accounts, credentials, irreversible actions, legal/platform risk,
  real technical blockers), MVP-first build discipline
  (MUST/SHOULD/SCALE-LATER), and the non-negotiables (identity consistency
  gate, no real-person likeness, Sofía-first).
- Added the commercial plan under `docs/business/`, running in parallel with
  the technical build from Day 0, not after it:
  - `GO_TO_MARKET.md` — MVP launch checklist, Day 0/7/14/30/60/90 plan,
    launch sequencing for the first grid posts, content pillars
    (reach/engagement/trust/conversion/retention), virality-hypothesis
    framework, competitive-benchmarking method, multi-influencer trigger.
  - `REVENUE_MODEL.md` — revenue streams (Fanvue, brand deals, affiliate,
    digital products, licensing), unit economics, conservative/base/aggressive
    scenarios at 30d/90d/6mo/12mo, milestone reverse-engineering from first
    revenue through €100k/mo, all assumptions explicitly labeled as
    assumptions to verify against real data, not forecasts.
  - `WEEKLY_OPS.md` — recurring BUILD/CREATE/PUBLISH/GROW/MONETIZE/MEASURE
    template and the North Star Metrics set.
- Added `docs/PHASE2_RUNBOOK.md` — the exact, ready-to-execute procedure to
  go from Sofía's Identity Pack to a locked canonical face at minimum cost,
  and `scripts/generate_candidates.py` — the actual Phase 2 zero-shot
  candidate-sweep script (fal.ai + FLUX-schnell, cost estimate ~€1-2 for 40
  candidates), fully built and unit-tested (dry-run verified) but requiring
  a funded fal.ai account to actually generate images.
- Updated `ROADMAP.md` (MUST/SHOULD/SCALE tags per phase, Phase 2 now points
  at the runbook), `COSTS.md` (added explicit Reinvestment policy section),
  `experiments/EXPERIMENT_LOG.md` (entries now require success/kill criteria
  defined before running), `README.md` (repo map, status, getting-started
  updated to match).
- 29 passing tests (added `tests/test_generate_candidates.py` for the new
  script's pure request-building logic).
- Still zero images generated, zero money spent, zero external accounts
  created. Single real blocker for Phase 2 execution: funding a fal.ai
  account (money + external account, owner's call, `CLAUDE.md` §3).

## 2026-08-11 — Phase 1: Identity design (Sofía / SOFIA_01)

- Ran the creative decision sequence for the first influencer (fitness +
  lifestyle) and consolidated it into a complete Identity Pack + Personality
  Bible at `influencers/sofia_01/`.
- Locked: Mediterranean archetype; Sofía, 24, española, Barcelona; deep
  mahogany/dark-auburn wavy hair (deliberately not bright red/orange); honey
  hazel eyes; natural toned athletic ("fitness natural") build; light natural
  freckles across nose/cheekbones as the fixed distinctive mark; clean-girl
  minimalist style (dewy natural makeup, white/beige/cream/black wardrobe
  palette, thin gold hoop earrings + fine chain as signature accessories).
- Remaining facial-geometry wording (face/nose/lip shape) written as
  generation-ready descriptors, intentionally not pixel-locked — per
  `IDENTITY_SYSTEM.md` §2 that gets fixed once a canonical face is chosen in
  Phase 2, not guessed in text now.
- Updated `README.md` (status + repo map) and `ROADMAP.md` (Phase 1 marked
  done with DoD checked, "Next execution" now points at the real Phase 2
  blocker) to stay consistent with the new influencer folder.
- Added a regression test loading the real `sofia_01/identity_pack.yaml`
  through `IdentityPack.from_yaml` to catch schema drift.
- Still zero images generated, zero money spent, zero external accounts
  created. Phase 2 (canonical face selection) is fully specified and ready,
  blocked only on a cloud-GPU-account decision that requires the owner's
  sign-off (money + external account).

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
