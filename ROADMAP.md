# Roadmap

Each phase must be **demonstrated working**, not just coded, before the next
starts. "Definition of Done" (DoD) is objective and checkable.

Every phase below is tagged against `CLAUDE.md` §5's build discipline:
**[MUST]** = required before Sofía's launch, **[CONDITIONAL]** = only
executed if a cheaper tier measurably didn't clear the bar (see
`IDENTITY_SYSTEM.md` §2a Progressive Identity Complexity Ladder — never
assumed necessary by default), **[SHOULD]** = worth it once there's real
engagement/revenue signal, **[SCALE]** = only once revenue justifies it. See
`docs/business/GO_TO_MARKET.md` §Launch Gate for the concrete, objective
launch checklist these map to, and `docs/PHASE2_RUNBOOK.md` for the exact,
ready-to-run procedure for the phase immediately ahead. Commercial work
(`docs/business/`) runs **in parallel** with the technical phases starting
Day 0 — it does not wait for Phase 9.

## Phase 0 — Research & Architecture ✅ [MUST] (this delivery)
**Goal:** Know exactly what we're building and why before spending a euro.
- DoD:
  - ✅ Stack decisions documented with rationale (`ARCHITECTURE.md`)
  - ✅ Full roadmap (this file)
  - ✅ Cost model (`COSTS.md`)
  - ✅ Identity system design (`IDENTITY_SYSTEM.md`)
  - ✅ Content pipeline design (`CONTENT_PIPELINE.md`)
  - ✅ Repo scaffold + prompt engine code with passing tests
  - ✅ No money spent, no external accounts created yet

## Phase 1 — Identity design ✅ [MUST]
**Goal:** Turn a creative brief into a structured, reusable Identity Pack —
before generating a single image.
- Work done: **Sofía (`SOFIA_01`)** — 24, española, Barcelona, fitness +
  lifestyle mediterráneo. Mediterranean archetype, deep mahogany wavy hair,
  honey-hazel eyes, natural toned fitness build, light freckles across
  nose/cheekbones as the fixed distinctive mark, clean-girl minimalist style
  (makeup/wardrobe palette/accessories). Full trait set in
  `influencers/sofia_01/identity_pack.yaml`; voice/interests/boundaries in
  `influencers/sofia_01/personality_bible.yaml`.
- DoD:
  - ✅ Identity Pack complete (all required fields filled; immutable facial/body
    traits separated from variable styling defaults per `IDENTITY_SYSTEM.md` §1)
  - ✅ Personality Bible complete
  - ✅ Codename `SOFIA_01`, version `v1` assigned, `influencers/sofia_01/` created
  - ✅ Zero images generated yet — this phase was pure specification
  - Fine facial geometry (exact face/nose/lip shape wording) is deliberately
    descriptive, not pixel-locked — it gets visually locked once a canonical
    image is chosen in Phase 2, per `IDENTITY_SYSTEM.md` §2

## Phase 2 — Canonical character (face selection) [MUST] ▶ next up
**Goal:** Pick ONE face and lock it as the ground truth, using cheap zero-shot
generation, before any training investment.
- Work: **fully scripted, see `docs/PHASE2_RUNBOOK.md` for the exact
  commands** — generate 30–60 zero-shot candidates from the Identity Pack
  description (serverless, ~€1–2 total, `scripts/generate_candidates.py`
  already written and tested), narrow to a shortlist, render the shortlist
  in controlled variations (frontal/3-4/profile, neutral/smile) with
  zero-shot identity conditioning, pick one.
- DoD:
  - One canonical frontal reference image selected and stored at
    `influencers/<codename>/versions/v1/canonical_refs/canonical_front.png`
  - Matching 3/4, profile, neutral and smiling variants generated from the
    same identity conditioning (visually the same person by manual review)
  - Cost logged in `experiments/EXPERIMENT_LOG.md`
  - Immediately followed by a Tier 1 attempt at Phase 5 (below) — no pause
    to "decide" whether to train, the test itself decides

## Phase 3 — Identity dataset [CONDITIONAL — Tier 2, only if Phase 5's Tier 1 attempt scores below 80]
**Goal:** Build the small, clean, high-signal image set the LoRA will train on.
- **Skipped entirely if the Tier 1 zero-shot Consistency Test (Phase 5)
  already cleared 80/100** — see `IDENTITY_SYSTEM.md` §2a. Do not start this
  phase pre-emptively "just in case."
- Work: expand canonical refs into the full dataset per `IDENTITY_SYSTEM.md`
  §Dataset spec (count, poses, lighting, framing), score every image with the
  scoring rubric, discard failures.
- DoD:
  - 20–40 images passing the per-image scoring rubric (≥ threshold defined in
    `IDENTITY_SYSTEM.md`)
  - Captions written for every kept image
  - Rejected-image log kept (what was excluded and why) for future learning

## Phase 4 — Identity training [CONDITIONAL — Tier 2, same trigger as Phase 3]
**Goal:** Train the FLUX LoRA that becomes the durable identity backbone.
- Same condition as Phase 3 — only reached if Tier 1 didn't clear the gate.
- Work: run training on rented GPU per hyperparameters in `IDENTITY_SYSTEM.md`
  §Training, checkpoint every N steps, keep the checkpoint that scores best in
  Phase 5, not just the last one.
- DoD:
  - LoRA file saved and versioned at `versions/v1/lora/`
  - Training config + cost logged in `experiments/EXPERIMENT_LOG.md`
  - At least 2 checkpoints compared, best one selected with justification

## Phase 5 — Consistency validation (gate — cannot be skipped) [MUST]
**Goal:** Prove the character survives real production variety before
building anything on top of it. **Runs at Tier 1 immediately after Phase 2**
(zero-shot only, no dataset/training needed to attempt it) — Phases 3/4 only
happen if this first attempt fails.
- Work: run the 15-shot Character Consistency Test (`IDENTITY_SYSTEM.md`
  §Consistency Test) using whichever tier is currently being evaluated,
  compute the Identity Consistency Score.
- DoD:
  - Score ≥ threshold (defined in `IDENTITY_SYSTEM.md`, currently 80/100)
  - All 15 test shots pass the AI-Artifact QA checklist
  - `consistency_report.md` written for this version, noting which tier passed
  - **If Tier 1 fails: proceed to Phase 3/4 (Tier 2), then re-run this exact
    test.** If Tier 2 also fails: escalate per `IDENTITY_SYSTEM.md` §2a Tier 3.
    Never proceed to Phase 6 without a passing score at some tier.

## Phase 6 — Production image pipeline [MUST, scoped to the Launch Gate]
**Goal:** Turn the validated identity into a repeatable generation pipeline —
scene/outfit/pose/camera/lighting all controllable via the prompt engine. At
MVP scope this only needs to produce the **20–30 images the Launch Gate
requires** (`docs/business/GO_TO_MARKET.md` §Launch Gate), covering the
photo styles the launch sequence actually uses — not the full style/location
library exhaustively (that breadth gets used over time, post-launch).
- Work: wire `engine/prompt_engine` to the cloud generation endpoint,
  implement pose ControlNet + garment conditioning (text + IP-Adapter image),
  implement location conditioning (`engine/locations`).
- DoD: generate a themed batch (e.g. "gym", "travel: Barcelona", "restaurant
  dinner") on demand from parameters only, each batch passing QA + identity
  score at the same bar as Phase 5, reaching 20–30 approved images total

## ✅ Launch Gate — see `docs/business/GO_TO_MARKET.md` §Launch Gate
Once Phase 6 has produced the 20–30 approved images and Phase 9's account
setup is done, check the Launch Gate table — if every item is ✅, **launch**,
don't keep iterating. This is the single authoritative go/no-go checklist;
not restated here to avoid two copies drifting out of sync.

## Phase 7 — Automated QA [SHOULD]
**Goal:** Reduce manual review load without lowering the quality bar. Manual
QA against the checklist (`IDENTITY_SYSTEM.md` §7) is enough at MVP volume —
this phase earns its keep once volume/growth signal makes manual triage the
bottleneck, not before.
- Work: automate face-similarity scoring, sharpness/artifact heuristics,
  aesthetic scoring, NSFW risk flagging; use scores to auto-sort/pre-filter,
  human makes the final call.
- DoD: a batch of 50 generations can be triaged (auto-reject obvious
  failures, auto-rank the rest) in under 5 minutes of human time

## Phase 8 — Content engine [SHOULD]
**Goal:** Go from "influencer + content type + location + outfit + mood" to a
finished, QA'd, captioned image with minimal manual prompt-writing. At MVP
scale, running the Phase 6 pipeline by hand per content-calendar entry is
fine — this phase is about removing manual work once cadence/volume demands it.
- DoD: a content calendar entry can be turned into 4–8 candidate images +
  caption draft via a single script invocation

## Phase 9 — Social publishing workflow [MUST: accounts + first posts live] [SHOULD: automation]
**Goal:** Get content onto Instagram/TikTok with the right AI-disclosure
compliance. Manual publishing is explicitly fine at MVP volume
(`COSTS.md` §What we do NOT pay for) — accounts existing and the launch
sequence (`docs/business/GO_TO_MARKET.md` §Launch sequencing) actually going
out is MUST; a mostly-automated publishing workflow is a SHOULD once cadence
makes manual publishing the bottleneck.
- 🔒 Requires: Instagram/TikTok creator accounts (external accounts — your call)
- DoD: a post can go from "approved in content/" to "published" (manually or
  automated) with disclosure requirements met

## Phase 10 — Analytics [MUST: minimal] [SHOULD: automated]
**Goal:** Know what's working. A manual metrics snapshot in
`docs/business/WEEKLY_OPS.md` is the MUST-have floor from Day 14 onward
(`docs/business/GO_TO_MARKET.md`); an automated pull into `content/metrics/`
is a SHOULD once manual tracking becomes the bottleneck.
- DoD: engagement/growth metrics pulled into `content/metrics/` on a
  schedule, tied back to content type/location/outfit tags so we can see
  which content patterns perform

## Phase 11 — Video [SCALE]
**Goal:** Extend the validated identity into short-form video, only after
image identity is rock solid AND there's growth/revenue signal justifying
the added production cost.
- Explicitly NOT started before Phase 5 gate is passed for at least one
  influencer. Re-research the video stack at this point — it moves too fast
  to decide now (see `ARCHITECTURE.md` §4 risks).

## Phase 12 — Multi-influencer scaling [SCALE]
**Goal:** Reproduce the whole pipeline for influencer #2, #3... without
multiplying manual work. Gated on the Multi-influencer trigger in
`docs/business/GO_TO_MARKET.md` §Multi-influencer trigger — consistent
production, reliable pipeline, real growth signal, first conversions — not
on a calendar date.
- DoD: a second influencer reaches its own Phase 5 gate using only the
  existing `engine/` tooling — zero engine code changes required, only new
  `influencers/<codename2>/` content

---

## Next execution

**Phase 1 is done.** Phase 2 (canonical face selection for Sofía) has its
exact procedure written and its generation script built and tested
(`docs/PHASE2_RUNBOOK.md`, `scripts/generate_candidates.py`) — ready to run
in minutes, immediately followed by a Tier 1 zero-shot attempt at Phase 5
(no dataset/training assumed necessary — `IDENTITY_SYSTEM.md` §2a). Phase
3/4 (dataset + LoRA training) only happen if that attempt scores below
80/100. It is blocked on exactly one thing: creating and funding a fal.ai
account (money + external account, owner's call, `CLAUDE.md` §3).

See `docs/business/GO_TO_MARKET.md` §Launch target for the aggressive-but-
realistic timeline (~10–14 days if Tier 1 clears the gate, ~18–21 days if
Tier 2/LoRA is needed) once execution resumes.

**In parallel, not blocked on anything:** `docs/business/GO_TO_MARKET.md`
Day 0 commercial prep (handle reservation needs Instagram/TikTok accounts —
also flagged) and content-pillar/launch-sequence planning can proceed
alongside Phase 2 once execution resumes.
