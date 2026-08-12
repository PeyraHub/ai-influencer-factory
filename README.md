# AI Influencer Factory

A production system for creating and operating hyperrealistic, fully original AI
influencers — consistent identity, repeatable content production, and a growth
+ monetization engine (Instagram/TikTok → brand deals → Fanvue) — built to run
on a **MacBook Pro Apple Silicon 16GB** at **€0–30/month** and scale up as
revenue allows.

This is not a demo. It is Phase 0 of a real business: infrastructure first,
one flawless character before content volume, content volume before growth
tactics, growth before monetization.

## North Star

```
HIPERREALISMO × IDENTIDAD CONSISTENTE × AUTOMATIZACIÓN × ESCALABILIDAD
```
subject to: cost(stage 1) ≤ €30/mo, runs on 16GB unified memory.

## Status

**Phase 1 complete — Identity design.** First influencer, **Sofía**
(`influencers/sofia_01/`), has a finished Identity Pack + Personality Bible:
Mediterranean archetype, mahogany wavy hair, honey-hazel eyes, natural toned
fitness build, light freckles, clean-girl minimalist style, Barcelona-based
fitness/lifestyle persona. No face has been generated yet. Phase 2 (canonical
face selection) has its exact procedure and generation script ready to run
(`docs/PHASE2_RUNBOOK.md`), blocked only on funding a fal.ai account
(money/external account, owner's call). See `ROADMAP.md` for the full phase
plan, `CLAUDE.md` for the standing operating rules this project runs under,
and `docs/business/` for the commercial plan running in parallel with the
technical build.

## Repo map

```
ai-influencer-factory/
├── CLAUDE.md                    Standing operating rules — autonomy, MVP discipline, budget, non-negotiables
├── README.md                    You are here
├── ARCHITECTURE.md              System design + every "option A vs B" decision, justified
├── ROADMAP.md                   Phase 0–12 plan, MUST/SHOULD/SCALE-tagged, with Definition of Done per phase
├── COSTS.md                     Budget stages, unit economics, cost formulas, reinvestment policy
├── IDENTITY_SYSTEM.md           Identity Pack spec, dataset rules, training strategy,
│                                 consistency test, AI-artifact QA checklist
├── CONTENT_PIPELINE.md          Prompt engine, photo-style library, locations,
│                                 clothing pipeline, content engine, publishing
├── CHANGELOG.md                 Chronological log of real changes
├── docs/
│   ├── research/                 Dated technology research snapshots (sources cited)
│   ├── PHASE2_RUNBOOK.md         Exact, ready-to-run procedure for the next milestone
│   └── business/                 GO_TO_MARKET.md · REVENUE_MODEL.md · WEEKLY_OPS.md — the commercial plan
├── influencers/
│   ├── _template/                Blank schema to copy for each new influencer
│   └── sofia_01/                 First influencer — Sofía, fitness + lifestyle, Barcelona
│       ├── identity_pack.yaml   Immutable + variable traits (the character's "constitution")
│       ├── personality_bible.yaml
│       └── versions/v1/         canonical_refs/ · dataset/ · lora/ (empty until Phase 2+)
├── engine/
│   ├── prompt_engine/           Modular prompt builder (identity+scene+outfit+pose+camera+…)
│   ├── identity/                Consistency scoring + AI-artifact QA checks
│   ├── styles/                  Reusable photography style library (iPhone selfie, gym, etc.)
│   └── locations/               Reusable location reference library
├── scripts/                     Ready-to-run phase scripts (e.g. generate_candidates.py, Phase 2)
├── content/                     calendar/ · captions/ · metrics/ (generated content lives outside git — see .gitignore)
├── experiments/EXPERIMENT_LOG.md  Every experiment + success/kill criteria, so we never repeat a failure
└── tests/                       pytest suite for engine code and scripts
```

## Principles this repo enforces

1. **Identity and QA outrank automation.** Nothing ships to a feed unless it
   passes the Identity Consistency Score threshold and the AI-Artifact QA
   checklist (`IDENTITY_SYSTEM.md`).
2. **Simple first, scalable later.** No dashboard, no orchestration platform,
   no multi-influencer abstraction until one influencer's pipeline is proven
   end-to-end (`ROADMAP.md` Definition of Done).
3. **Local when viable, cloud when it buys a real advantage.** Orchestration,
   prompt building, QA scoring, upscaling and organization run on the Mac.
   LoRA training and heavy FLUX inference run on rented cloud GPU, billed by
   the minute, never idle.
4. **No secrets in git.** All credentials via `.env` (see `.env.example`),
   `.env` is gitignored.
5. **No real-person likeness.** Every influencer is an original identity. See
   `IDENTITY_SYSTEM.md` §"Ethics & platform compliance".

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in API keys — never commit this file
pytest                 # engine/ + scripts/ unit tests (prompt engine, QA heuristics)

# Only needed to actually run Phase 2 generation (docs/PHASE2_RUNBOOK.md):
pip install -e ".[generation]"
python scripts/generate_candidates.py --identity influencers/sofia_01/identity_pack.yaml --count 6 --dry-run
```

## Where things stand / what's next

See `ROADMAP.md` → "Next execution" for the exact next step and
`CHANGELOG.md` for what has actually been built and tested so far.
