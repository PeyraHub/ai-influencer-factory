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
fitness/lifestyle persona. No face has been generated yet — that's Phase 2,
currently blocked on a cloud-GPU-account decision (money/external account,
owner's call, not mine to make). See `ROADMAP.md` for the full phase plan and
`docs/research/stack_research_2026.md` for the technology comparison behind
every architecture decision.

## Repo map

```
ai-influencer-factory/
├── README.md                    You are here
├── ARCHITECTURE.md              System design + every "option A vs B" decision, justified
├── ROADMAP.md                   Phase 0–12 plan with Definition of Done per phase
├── COSTS.md                     Budget stages, unit economics, cost formulas
├── IDENTITY_SYSTEM.md           Identity Pack spec, dataset rules, training strategy,
│                                 consistency test, AI-artifact QA checklist
├── CONTENT_PIPELINE.md          Prompt engine, photo-style library, locations,
│                                 clothing pipeline, content engine, publishing
├── CHANGELOG.md                 Chronological log of real changes
├── docs/research/               Dated technology research snapshots (sources cited)
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
├── content/                     calendar/ · captions/ · metrics/ (generated content lives outside git — see .gitignore)
├── experiments/EXPERIMENT_LOG.md  Every training/generation experiment, so we never repeat a failure
└── tests/                       pytest suite for engine code
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

## Getting started (once Phase 1 begins)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in API keys — never commit this file
pytest                 # engine/ unit tests (prompt engine, QA heuristics)
```

## Where things stand / what's next

See `ROADMAP.md` → "Next execution" for the exact next step and
`CHANGELOG.md` for what has actually been built and tested so far.
