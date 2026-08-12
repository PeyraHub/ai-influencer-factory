# Phase 2 Runbook — Sofía canonical face selection

**Purpose:** the exact, ready-to-execute path from the finished Identity Pack
(`influencers/sofia_01/identity_pack.yaml`) to one locked canonical face, at
minimum cost and zero unnecessary infrastructure. Written so that the moment
the one real blocker (a funded fal.ai account) is cleared, execution takes
minutes, not another research pass. See `IDENTITY_SYSTEM.md` §2 for the
underlying design rationale — this document is the "just run it" version.

## Why fal.ai, and why not assume training is needed

At Phase 2 there is no reference face to condition on — the goal *is* to
create the first one. So this phase starts with **plain text-to-image**, not
identity-conditioned generation, and — critically — **does not assume LoRA
training is the destination**. Per `IDENTITY_SYSTEM.md` §2a (Progressive
Identity Complexity Ladder), the plan is:

1. Generate a wide batch of candidate faces from `identity_pack.yaml`'s
   `descriptor_fragments` alone (no conditioning — no face exists yet).
2. Human picks the best candidate(s) — genuinely subjective, the owner's call.
3. Cheap variation check on the shortlist, then pick ONE final candidate.
4. Run the **full 15-shot Character Consistency Test** on that one candidate
   using zero-shot conditioning only (Tier 1 — no dataset, no training).
5. **Score it.** If it clears 80/100, that's the production identity method,
   done — Phases 3/4 (dataset + LoRA training) never happen. Only escalate
   to Tier 2 if the measured score says Tier 1 wasn't enough.

fal.ai is the pick over RunPod for this phase specifically because it's
serverless (pay per image, zero idle cost, zero pod setup) and this phase is
low-volume, high-iteration — exactly what serverless is for
(`ARCHITECTURE.md` §2.4, §2.6).

## Exact steps

### 1. Account + credential (🔒 the actual blocker — owner action)
- Create a fal.ai account at fal.ai, attach a payment method.
- Generate an API key from the fal.ai dashboard.
- Put it in `.env` (never commit): `FAL_KEY=...` (this is the exact
  environment variable name the fal.ai Python client reads automatically —
  verified against current fal.ai docs, not `FAL_API_KEY`)
- **Hard spend cap: EUR 3.00 for this entire Tier 1 attempt**, enforced in
  code (`engine/budget_guard.py`), not just documentation. Both generation
  scripts reserve their estimated cost against a shared
  `influencers/sofia_01/versions/v1/.spend_ledger.json` ledger (label
  `"tier1"`) *before* calling fal.ai, and refuse to proceed once cumulative
  reserved spend would cross the cap — cumulative across every invocation of
  either script, not reset per run. Exceeding it requires passing
  `--i-authorize-overage` explicitly, which is a deliberate owner decision,
  never a default.
- **Verified real cost** (fal.ai pricing docs, checked 2026-08; both scripts
  request an explicit 768×1024 / 0.786 MP image, billed as 1 MP rounded up):
  - `fal-ai/flux/schnell` (candidate sweep): **$0.003/image** → 40 images ≈ **€0.12**
  - `fal-ai/flux-pulid` (shortlist checks + full test): **$0.0333/image**
  - Full Tier 1 attempt (40 candidates + 5×3 shortlist shots + 15-shot test):
    **≈ €1.12 total** — well under the €3 cap, leaving headroom for a re-run
    if a batch needs redoing. (Cost tracked as EUR 1:1 with USD, a
    deliberately conservative simplification — see `engine/budget_guard.py`.)
  - If Tier 1 clears the gate, **€1.12 is the entire identity cost** — no
    training spend at all.

### 2. Sanity-check with 1–2 images FIRST, then the full sweep (`scripts/generate_candidates.py`)
```bash
source .venv/bin/activate
pip install -e ".[generation]"     # adds fal-client, only needed for this step

# MANDATORY first command — not optional. Confirms the API key, the fal.ai
# call, and the download path all work before spending on the full batch.
python scripts/generate_candidates.py --identity influencers/sofia_01/identity_pack.yaml --count 2
# Inspect influencers/sofia_01/versions/v1/candidates/ — 2 images, look sane? Then:

python scripts/generate_candidates.py --identity influencers/sofia_01/identity_pack.yaml --count 38 --seed-start 2
```
- Uses FLUX.1-schnell (cheapest, fastest FLUX variant) via fal.ai for the
  wide sweep — quality is sufficient for face/shape selection at this stage;
  the final chosen candidate gets re-rendered at higher quality in step 4.
- Pulls `descriptor_fragments` straight from the Identity Pack via
  `engine.prompt_engine`, varies `photo_style` (iphone_selfie,
  professional_campaign, mirror_selfie) and seed across the batch for real
  variety, not 40 near-duplicates.
- Saves images + a metadata JSON (seed, style, prompt, cost) to
  `influencers/sofia_01/versions/v1/candidates/` (gitignored, like all
  generated media). The 2-image test and the 38-image follow-up both write
  to the same `.spend_ledger.json` — the test's cost still counts.

**Execution protocol once the key is available:** run the 2-image test: if
both images download successfully and look like reasonable renders of the
Identity Pack description (no API errors, no garbage output), proceed
autonomously through the rest of this runbook — the remaining 38 candidates,
all shortlist checks, the full 15-shot test — without asking again at each
step. Stop only at step 3 (picking favorites from the candidate sheet) and
step 5 (final candidate pick), which are the genuinely subjective calls this
runbook can't make. If the 2-image test fails (API error, no output, ledger
cap issue), stop and report that specific failure rather than retrying blindly.

### 3. Human selection (your call — genuinely subjective, not automatable)
- Review the 40-image contact sheet.
- Shortlist 3–5 that most match the Identity Pack description and that you'd
  actually want as the face of the brand.
- No tooling needed for this step beyond looking at the images.

### 4. Cheap shortlist check (already scripted — `scripts/generate_variations.py`)
```bash
python scripts/generate_variations.py --identity influencers/sofia_01/identity_pack.yaml \
    --reference influencers/sofia_01/versions/v1/candidates/<chosen_file>.png \
    --shots selfie,professional,smiling
```
- Run once per shortlisted candidate (3–5 times, ~€0.10 each — trivial).
- Uses `fal-ai/flux-pulid` (zero-shot identity conditioning, no training) to
  check the face survives 3 quick angle/expression changes before spending
  on the full test. Eliminates obviously-weak candidates cheaply.

### 5. Final pick + canonical refs
- Pick ONE final candidate whose quick variations hold up (your call).
- Copy/rename its images into
  `influencers/sofia_01/versions/v1/canonical_refs/` following the naming in
  `IDENTITY_SYSTEM.md` §2 (`canonical_front.png` at minimum).
- Update `influencers/sofia_01/identity_pack.yaml`:
  `status: "canonical_selected"`, confirm `generation_conditioning.pulid_reference_image`
  points at the real file.

### 6. Full 15-shot Consistency Test — Tier 1 attempt (`scripts/generate_variations.py --shots all`)
```bash
python scripts/generate_variations.py --identity influencers/sofia_01/identity_pack.yaml \
    --reference influencers/sofia_01/versions/v1/canonical_refs/canonical_front.png \
    --shots all \
    --out-dir influencers/sofia_01/versions/v1/consistency_test
```
- Generates all 15 conditions from `IDENTITY_SYSTEM.md` §6, ~€0.50 total,
  still zero-shot, still no training.
- Also manually review these 15 images against the AI-Artifact QA checklist
  (`IDENTITY_SYSTEM.md` §7) — the Consistency Score alone isn't the whole gate.

### 7. Score it (`scripts/score_consistency.py`)
```bash
cp influencers/_template/manual_consistency_scores.yaml \
   influencers/sofia_01/versions/v1/manual_consistency_scores.yaml
# ...fill in the 3 manual sub-scores after reviewing the 15 shots...
pip install -e ".[identity]"     # adds insightface, only needed for this step
python scripts/score_consistency.py \
    --shots-dir influencers/sofia_01/versions/v1/consistency_test \
    --canonical-ref influencers/sofia_01/versions/v1/canonical_refs/canonical_front.png \
    --manual-scores influencers/sofia_01/versions/v1/manual_consistency_scores.yaml \
    --tier 1
```
- Prints and writes `consistency_report.md` with the final 0–100 score.
- **Score ≥ 80 → identity locked at Tier 1.** Skip Phases 3/4 entirely,
  go straight to Phase 6 (production pipeline) using this same zero-shot
  conditioning. This is the outcome to hope for — it's strictly less work.
- **Score < 80 → escalate to Tier 2**: build the dataset (Phase 3,
  `IDENTITY_SYSTEM.md` §3) and train a LoRA (Phase 4, §5), then re-run steps
  6–7 with the trained identity conditioning instead.

### 8. Log it
- Add entries to `experiments/EXPERIMENT_LOG.md` for the candidate sweep, the
  shortlist checks, and the scored Consistency Test — config, seeds, cost,
  score, tier, result — using these criteria:
  - **Success criterion (candidate sweep):** at least one candidate clearly
    matches the Identity Pack description and is genuinely appealing/on-brand.
  - **Kill criterion (candidate sweep):** zero acceptable candidates after 60
    total generations across 2 prompt phrasings — revise `descriptor_fragments`
    wording before generating more blindly.
  - **Success criterion (Tier 1 consistency test):** score ≥ 80/100.
  - **Kill criterion (Tier 1):** none — a fail here isn't a dead end, it's the
    signal to escalate to Tier 2, which is exactly what the ladder is for.

## What happens after this runbook

If Tier 1 passes: Phase 6 (production pipeline) starts directly — no dataset,
no training. If Tier 1 doesn't clear the gate: Phase 3 (dataset) and Phase 4
(LoRA training) are already fully specified in `IDENTITY_SYSTEM.md` §3–§5,
followed by re-running steps 6–7 above with the trained identity. Either way,
Phase 5's gate (`IDENTITY_SYSTEM.md` §6) is what decides — not an assumption
made here.
