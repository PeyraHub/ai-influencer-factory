# CLAUDE.md — Permanent operating rules for this project

This file governs how Claude works on `ai-influencer-factory` in **every**
session, including after a session renewal/context reset. It is the
project's standing instruction set — read it before doing anything else.
It does not expire and does not need to be re-stated by the user.

If anything here appears to conflict with a specific user message in a given
session, the live message wins for that session, but this file is the
default to return to once that instruction is fulfilled.

## 0. What this project is

A scalable hyperrealistic AI-influencer business, built by one person on a
MacBook Pro 16GB, starting at €0–30/mo. Not an art project. Read `README.md`,
`ARCHITECTURE.md`, `ROADMAP.md`, `IDENTITY_SYSTEM.md`, `COSTS.md` and
`docs/business/` for the full technical and commercial design before making
non-trivial changes — they contain the reasoning, not just the conclusions.

## 1. North Star

```
LAUNCH ASAP → LEARN ASAP → REVENUE ASAP → SCALE WHAT WORKS
```
optimized against **Time To First Publishable Influencer**, then
**Time To First Revenue** — never against technical elegance for its own
sake. Be ambitious about the business's ceiling; be strictly realistic about
costs, probabilities, and what current data actually supports. An aggressive
target is a target, never a forecast presented as guaranteed.

## 2. Non-negotiables (never traded away for speed)

- **Identity consistency and hyperrealism are requirements, not nice-to-haves.**
  The Phase 5 Identity Consistency Score gate (`IDENTITY_SYSTEM.md` §6,
  threshold 80/100) is never skipped or lowered to hit a launch date. A fast
  launch with a character that doesn't hold together is worse than no launch.
- No real person's likeness, no deepfakes, no impersonation (`IDENTITY_SYSTEM.md` §8).
- No secrets committed to git; `.env` only (`.env.example` kept current).
- Sofía first. No second influencer until Sofía has validated the pipeline
  end-to-end (content consistent, publishing working, growth signal,
  first conversions) — see `docs/business/GO_TO_MARKET.md` for the
  multi-influencer trigger condition.

## 3. Autonomy — maximize useful progress per user turn

Default posture: **analysis → several decisions → implementation → tests →
docs → commit → push → next executable block**, all in one pass, without
stopping in between. If 5, 10, or 20 related actions can be done without new
input from the user, do them all before stopping.

**Never stop to ask about:** folder structure, technical naming, library
choices, tests, documentation, refactors, config, scripts, or picking
between technical alternatives when one is clearly better. Investigate and
resolve technical blockers yourself before considering them a reason to stop.

**Only stop to ask when one of these is genuinely true:**
1. A creative decision that permanently defines the influencer (face, body,
   personality-defining traits — not styling details).
2. Spending real money.
3. Creating an external account.
4. Needing an API key or credential you don't have.
5. An irreversible or hard-to-reverse action.
6. Meaningful legal/platform-policy risk.
7. A real technical blocker you cannot resolve after investigating.

Do not ask "should I continue?" if you can continue. Do not ask "should I
create X?" if X is already part of the approved roadmap/plan. Do not end a
phase just because code was written — also run tests, validate, update docs,
commit, and push, then move to the next actionable block, before stopping.

## 4. When you do have to stop — format

No long write-ups. Exactly this, nothing else:

```
## BLOQUEO
[what you need]

## POR QUÉ
[max 2-3 sentences]

## QUÉ TENGO QUE HACER
[exact steps]

## COSTE
[if any]

## QUÉ HARÁS DESPUÉS
[one sentence]
```

## 5. Build discipline — MVP first, no premature infrastructure

Every phase/feature gets bucketed before being built:

- **MUST HAVE BEFORE LAUNCH** — required to publish Sofía's first content
- **SHOULD HAVE AFTER VALIDATION** — worth it once there's real engagement/revenue signal
- **SCALE LATER** — only makes sense once revenue justifies it (dashboards,
  multi-user systems, sophisticated automation, advanced video, multiple
  influencers, complex analytics)

See `ROADMAP.md` for the phase-by-phase bucketing and `docs/business/GO_TO_MARKET.md`
§MVP for the concrete launch checklist. When a new feature is proposed,
justify it as `Expected Impact / Time / Cost` against: quality, launch
speed, growth, monetization, manual-work reduction (in that priority order).
A feature that takes 5 days and doesn't clearly serve one of those does not
get built yet.

## 6. Budget

Current: **€0–30/month** (`COSTS.md` Stage 1). Do not exceed it without
explicit approval — creating a paid account or spending money is always a
stop-and-ask condition (§3 above), regardless of how small. Reinvestment
policy for scaling spend as revenue arrives is defined in `COSTS.md`
§Reinvestment policy — follow it rather than re-negotiating the budget ad hoc.

## 7. Cheap-first experimentation discipline

Before spending €100 perfecting something, run a €1–5 experiment. Before
generating 1,000 images, generate 8. Before training 10 LoRAs, train 1.
Before launching 5 influencers, prove Sofía works. Every significant
experiment gets a **success criterion** and a **kill criterion** written
down in `experiments/EXPERIMENT_LOG.md` *before* running it — see that
file's template. Don't keep running a format/strategy that has repeatedly
underperformed out of attachment to it.

## 8. Where things live

- Technical architecture & decisions: `ARCHITECTURE.md`
- Phase plan + Definition of Done: `ROADMAP.md`
- Identity system (the character's "constitution"): `IDENTITY_SYSTEM.md`
- Content/prompt pipeline: `CONTENT_PIPELINE.md`
- Budget, unit economics, reinvestment policy: `COSTS.md`
- Commercial plan (GTM, revenue model, weekly ops, north star metrics):
  `docs/business/`
- Ready-to-execute runbooks for the next concrete milestone: `docs/*_RUNBOOK.md`
- What actually happened, chronologically: `CHANGELOG.md`
- Every experiment, its config, cost, and result: `experiments/EXPERIMENT_LOG.md`

Keep all of these current as work happens — a doc that's stale the moment
it's written is worse than no doc, because it actively misleads whoever
(human or Claude) reads it next.
