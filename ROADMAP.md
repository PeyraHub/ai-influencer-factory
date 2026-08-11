# Roadmap

Each phase must be **demonstrated working**, not just coded, before the next
starts. "Definition of Done" (DoD) is objective and checkable.

## Phase 0 — Research & Architecture ✅ (this delivery)
**Goal:** Know exactly what we're building and why before spending a euro.
- DoD:
  - ✅ Stack decisions documented with rationale (`ARCHITECTURE.md`)
  - ✅ Full roadmap (this file)
  - ✅ Cost model (`COSTS.md`)
  - ✅ Identity system design (`IDENTITY_SYSTEM.md`)
  - ✅ Content pipeline design (`CONTENT_PIPELINE.md`)
  - ✅ Repo scaffold + prompt engine code with passing tests
  - ✅ No money spent, no external accounts created yet

## Phase 1 — Identity design
**Goal:** Turn a creative brief into a structured, reusable Identity Pack —
before generating a single image.
- Work: fill `influencers/<codename>/identity_pack.yaml` and
  `personality_bible.yaml` from your creative decisions (grouped questions at
  the end of this delivery); define immutable vs. variable traits explicitly.
- DoD:
  - Identity Pack complete (all required fields in the template filled)
  - Personality Bible complete
  - Codename + version (`v1`) assigned, folder created
  - Zero images generated yet (this phase is pure specification)

## Phase 2 — Canonical character (face selection)
**Goal:** Pick ONE face and lock it as the ground truth, using cheap zero-shot
generation (PuLID/InstantID), before any training investment.
- Work: generate 30–60 zero-shot candidates from the Identity Pack description
  (serverless, ~€1–2 total), narrow to a shortlist, render the shortlist in
  3–4 controlled variations each (frontal/3-4/profile, neutral/smile), pick one.
- DoD:
  - One canonical frontal reference image selected and stored at
    `influencers/<codename>/versions/v1/canonical_refs/canonical_front.png`
  - Matching 3/4, profile, neutral and smiling variants generated from the
    same seed/identity conditioning (visually the same person by manual review)
  - Cost logged in `experiments/EXPERIMENT_LOG.md`

## Phase 3 — Identity dataset
**Goal:** Build the small, clean, high-signal image set the LoRA will train on.
- Work: expand canonical refs into the full dataset per `IDENTITY_SYSTEM.md`
  §Dataset spec (count, poses, lighting, framing), score every image with the
  scoring rubric, discard failures.
- DoD:
  - 20–40 images passing the per-image scoring rubric (≥ threshold defined in
    `IDENTITY_SYSTEM.md`)
  - Captions written for every kept image
  - Rejected-image log kept (what was excluded and why) for future learning

## Phase 4 — Identity training
**Goal:** Train the FLUX LoRA that becomes the durable identity backbone.
- Work: run training on rented GPU per hyperparameters in `IDENTITY_SYSTEM.md`
  §Training, checkpoint every N steps, keep the checkpoint that scores best in
  Phase 5, not just the last one.
- DoD:
  - LoRA file saved and versioned at `versions/v1/lora/`
  - Training config + cost logged in `experiments/EXPERIMENT_LOG.md`
  - At least 2 checkpoints compared, best one selected with justification

## Phase 5 — Consistency validation (gate — cannot be skipped)
**Goal:** Prove the character survives real production variety before
building anything on top of it.
- Work: run the 15-shot Character Consistency Test (`IDENTITY_SYSTEM.md`
  §Consistency Test), compute the Identity Consistency Score.
- DoD:
  - Score ≥ threshold (defined in `IDENTITY_SYSTEM.md`, currently 80/100)
  - All 15 test shots pass the AI-Artifact QA checklist
  - `consistency_report.md` written for this version
  - **If this gate fails: return to Phase 3/4, do not proceed.** No exceptions.

## Phase 6 — Production image pipeline
**Goal:** Turn the validated identity into a repeatable generation pipeline —
scene/outfit/pose/camera/lighting all controllable via the prompt engine.
- Work: wire `engine/prompt_engine` to the cloud generation endpoint,
  implement pose ControlNet + garment conditioning (text + IP-Adapter image),
  implement location conditioning (`engine/locations`).
- DoD: generate a themed batch (e.g. "gym", "travel: Barcelona", "restaurant
  dinner") on demand from parameters only, each batch passing QA + identity
  score at the same bar as Phase 5

## Phase 7 — Automated QA
**Goal:** Reduce manual review load without lowering the quality bar.
- Work: automate face-similarity scoring, sharpness/artifact heuristics,
  aesthetic scoring, NSFW risk flagging; use scores to auto-sort/pre-filter,
  human makes the final call.
- DoD: a batch of 50 generations can be triaged (auto-reject obvious
  failures, auto-rank the rest) in under 5 minutes of human time

## Phase 8 — Content engine
**Goal:** Go from "influencer + content type + location + outfit + mood" to a
finished, QA'd, captioned image with minimal manual prompt-writing.
- DoD: a content calendar entry can be turned into 4–8 candidate images +
  caption draft via a single script invocation

## Phase 9 — Social publishing workflow
**Goal:** Get content onto Instagram/TikTok with the right AI-disclosure
compliance, minimal manual steps.
- 🔒 Requires: Instagram/TikTok creator accounts (external accounts — your call)
- DoD: a post can go from "approved in content/" to "published" via a
  documented, mostly-automated workflow, disclosure requirements met

## Phase 10 — Analytics
**Goal:** Know what's working.
- DoD: engagement/growth metrics pulled into `content/metrics/` on a
  schedule, tied back to content type/location/outfit tags so we can see
  which content patterns perform

## Phase 11 — Video
**Goal:** Extend the validated identity into short-form video, only after
image identity is rock solid.
- Explicitly NOT started before Phase 5 gate is passed for at least one
  influencer. Re-research the video stack at this point — it moves too fast
  to decide now (see `ARCHITECTURE.md` §4 risks).

## Phase 12 — Multi-influencer scaling
**Goal:** Reproduce the whole pipeline for influencer #2, #3... without
multiplying manual work.
- DoD: a second influencer reaches its own Phase 5 gate using only the
  existing `engine/` tooling — zero engine code changes required, only new
  `influencers/<codename2>/` content

---

## Next execution

**Phase 1 starts as soon as you answer the grouped questions at the end of
this delivery** (character concept + the one external-account/money decision
for cloud GPU access). Everything else in Phase 0 is done and pushed.
