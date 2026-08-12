# Phase 2 Runbook — Sofía canonical face selection

**Purpose:** the exact, ready-to-execute path from the finished Identity Pack
(`influencers/sofia_01/identity_pack.yaml`) to one locked canonical face, at
minimum cost and zero unnecessary infrastructure. Written so that the moment
the one real blocker (a funded fal.ai account) is cleared, execution takes
minutes, not another research pass. See `IDENTITY_SYSTEM.md` §2 for the
underlying design rationale — this document is the "just run it" version.

## Why fal.ai, and why not train/condition anything yet

At Phase 2 there is no reference face to condition on — the goal *is* to
create the first one. So this phase is **plain text-to-image**, not
identity-conditioned generation:

1. Generate a wide batch of candidate faces from `identity_pack.yaml`'s
   `descriptor_fragments` alone (no LoRA, no PuLID — those need an existing
   face to lock onto, which doesn't exist yet).
2. Human picks the best candidate(s) — genuinely subjective, the owner's call.
3. **Only then** does PuLID-Flux-II get used — conditioned on the *chosen*
   candidate, to confirm that exact face survives angle/expression changes
   (frontal/3-4/profile/smile/neutral) before any training investment.

fal.ai is the pick over RunPod for this phase specifically because it's
serverless (pay per image, zero idle cost, zero pod setup) and this phase is
low-volume, high-iteration — exactly what serverless is for
(`ARCHITECTURE.md` §2.4, §2.6).

## Exact steps

### 1. Account + credential (🔒 the actual blocker — owner action)
- Create a fal.ai account at fal.ai, attach a payment method.
- Generate an API key from the fal.ai dashboard.
- Put it in `.env` (never commit): `FAL_API_KEY=...`
- Estimated spend for all of Phase 2 (steps 2–4 below): **€2–4 total**
  (COSTS.md Phase 2/Phase 3 estimates), comfortably inside the €0–30/mo budget.

### 2. Wide candidate sweep (already scripted — `scripts/generate_candidates.py`)
```bash
source .venv/bin/activate
pip install -e ".[generation]"     # adds fal-client, only needed for this step
python scripts/generate_candidates.py --identity influencers/sofia_01/identity_pack.yaml --count 40
```
- Uses FLUX.1-schnell (cheapest, fastest FLUX variant) via fal.ai for the
  wide sweep — quality is sufficient for face/shape selection at this stage;
  the final chosen candidate gets re-rendered at higher quality in step 3.
- Pulls `descriptor_fragments` straight from the Identity Pack via
  `engine.prompt_engine`, varies `photo_style` (iphone_selfie,
  professional_campaign, mirror_selfie) and seed across the batch for real
  variety, not 40 near-duplicates.
- Saves images + a metadata JSON (seed, style, prompt, cost) to
  `influencers/sofia_01/versions/v1/candidates/` (gitignored, like all
  generated media).

### 3. Human selection (your call — genuinely subjective, not automatable)
- Review the 40-image contact sheet.
- Shortlist 3–5 that most match the Identity Pack description and that you'd
  actually want as the face of the brand.
- No tooling needed for this step beyond looking at the images.

### 4. Controlled variations per shortlisted candidate (PuLID-Flux-II)
```bash
python scripts/generate_variations.py --identity influencers/sofia_01/identity_pack.yaml \
    --reference influencers/sofia_01/versions/v1/candidates/<chosen_file>.png \
    --variations frontal,three_quarter,profile,smile,neutral
```
- *(This script is the next one to write — deliberately not built in this
  pass, since it's only needed once step 3 has actually produced a shortlist;
  building it earlier would be exactly the premature-infrastructure pattern
  `CLAUDE.md` §5 warns against.)*
- For each of the 3–5 shortlisted candidates, generates the controlled
  variation set — checks the face survives angle/expression changes
  zero-shot, per `IDENTITY_SYSTEM.md` §2, before any LoRA training spend.

### 5. Final pick + canonical refs
- Pick ONE final candidate whose variations hold up.
- Copy/rename its images into
  `influencers/sofia_01/versions/v1/canonical_refs/` following the naming in
  `IDENTITY_SYSTEM.md` §2 (`canonical_front.png` + 3/4, profile, smile,
  neutral, close-up, full-body, 2 lighting setups).
- Update `influencers/sofia_01/identity_pack.yaml`:
  `status: "canonical_selected"`, confirm `generation_conditioning.pulid_reference_image`
  points at the real file.

### 6. Log it
- Add an entry to `experiments/EXPERIMENT_LOG.md` for the sweep and for the
  variation runs — config, seeds, cost, result — using this phase's criteria:
  - **Success criterion:** at least one of the candidates clearly matches the
    Identity Pack description and is genuinely appealing/on-brand to the owner.
  - **Kill criterion:** zero acceptable candidates after 60 total generations
    across 2 different prompt phrasings — stop and revise
    `descriptor_fragments` wording before generating more blindly, don't just
    keep spending on volume.

## What happens after this runbook

Phase 3 (dataset) and Phase 4 (LoRA training) follow directly from the
canonical refs this produces — both already fully specified in
`IDENTITY_SYSTEM.md` §3–§5, no further planning needed, just execution once
Phase 2's canonical face is locked.
