# Identity System

This is the core IP of the business. Everything else (content, growth,
monetization) depends on the character actually being recognizable as the
same person across arbitrary scenes. This document defines how identity is
specified, built, measured, and protected.

## 1. Identity Pack

Every influencer has an `identity_pack.yaml` (template at
`influencers/_template/identity_pack.yaml`). Its single most important job is
separating **immutable** traits (the character's actual identity — never
allowed to drift) from **variable** traits (styling choices that change
photo-to-photo and must NOT get baked into the LoRA as if they were identity).

### Immutable (identity-defining — trained into the LoRA, referenced every generation)
- Face geometry: face shape, jaw/chin structure, cheekbone prominence
- Eyes: shape, color, spacing, eyebrow shape/thickness
- Nose: shape, bridge, width
- Lips: shape, fullness, philtrum
- Skin: base tone, undertone, texture (pores, fine lines — realism, not
  "airbrushed"), any fixed marks (specific freckle pattern, a mole in a
  specific place) — fixed marks are a *feature*: they're strong evidence the
  Identity Consistency check is passing, not a flaw to remove
- Body: height (apparent), frame/proportions, shoulder-to-hip ratio, natural
  body composition — the "canonical body reference" (§4)
- Hands: general shape/proportions (not manicure — that's variable)
- Age-appearance bracket (e.g. "late 20s") — must not visibly drift younger/older

### Variable (styling — controlled per-generation via the prompt engine, never
trained as if permanent)
- Hair color/length/style (unless the brief defines one signature hairstyle —
  even then, treat color/style as "usual" not "only possible")
- Makeup
- Nails
- Outfit / wardrobe
- Accessories (jewelry, glasses, watches)
- Pose, expression
- Location, background, lighting, camera/lens, time of day

**Why this split matters:** if training images all happen to share, say, a
messy bun and gym clothes, a LoRA will silently learn "messy bun + gym
clothes" as part of the identity, and every generation will fight you to
reproduce them regardless of prompt. Dataset construction (§3) exists
specifically to prevent this by forcing variation in every *variable* field
while holding every *immutable* field constant.

### Identity Pack fields (see template for the literal schema)
name, apparent age, nationality/background, backstory (2–3 sentences,
enough for personality consistency, not a novel), the full immutable trait
list above written out in plain language + as generation-ready descriptor
fragments (short phrases the prompt engine can compose directly), the
variable trait *defaults* (a "usual" look, since 100%-random styling every
post doesn't read as one consistent person's aesthetic either), recurring
signature elements (a specific accessory, a specific gym, a color palette
she gravitates to) — these live in `personality_bible.yaml`, not here, since
they're about brand/style consistency, not facial identity.

## 2. Canonical character creation pipeline

```
concept (Identity Pack draft, Phase 1)
   → zero-shot exploration: 30–60 candidate faces via PuLID-Flux-II/InstantID,
     no training, cheap, serverless (Phase 2)
   → shortlist 3–5 candidates, generate each in 4 controlled variations
     (frontal / 3-4 / profile, neutral / smile) to check the face survives
     angle changes even before training
   → pick ONE canonical identity (your call — this is subjective and about
     the character, so it's a decision for you, not for me to make alone)
   → canonical reference set generated from the chosen seed/conditioning:
     frontal, 3/4, profile, smiling, neutral, close-up, full-body, 2 lighting
     setups (soft/hard) — all still zero-shot, still cheap
   → dataset expansion from these canonical refs (Phase 3, §3)
   → dataset cleaning/scoring (§3)
   → LoRA training (Phase 4, §5)
   → Consistency Test + Identity Consistency Score (Phase 5, §6) — gate
```

This avoids the classic failure mode named in the brief: training on 50
incoherent images of a person who doesn't visually exist yet. We lock a face
*first*, cheaply, and only invest in training once that face has already
proven it survives basic angle/expression changes zero-shot.

## 3. Dataset

### Spec
| Parameter | Value | Why |
|---|---|---|
| Image count | 25–35 | Enough for a FLUX LoRA to generalize pose/lighting without overfitting; more than ~40 on a small, deliberately-varied set adds diminishing returns and more cleaning burden |
| Resolution | 1024×1024 (or matching FLUX training res) | Matches FLUX's native training resolution; upscale only if source is short, never train on upscaled-blurry images |
| Framing mix | ~40% face/close-up, ~35% half-body, ~25% full-body | Needs enough close-up density for facial fidelity, enough full-body for the canonical body reference (§4) to train too |
| Pose/angle variety | frontal, 3/4 left, 3/4 right, profile, looking down/up, seated, standing, walking | Forces the LoRA to learn geometry, not a single fixed angle |
| Expression variety | neutral, soft smile, full smile, laughing, serious/focused | Prevents "one expression baked in" |
| Lighting variety | soft daylight, harsh direct, golden hour, indoor artificial, overcast | Prevents lighting from being learned as identity |
| Background variety | at least 4 distinct plain/simple backgrounds | Prevents background from being learned as identity |
| Outfit variety | at least 4 distinct outfits, spanning at least 2 categories (e.g. athletic + casual) | Prevents one outfit from being learned as identity |
| Hair variety | at least 2 styles if the character's brief allows it, otherwise 1 consistent style but vary how it's lit/framed | Prevents "hair state" over-fitting when only 1 style is canonical |

### Captioning
Every kept image gets a short caption describing only the **variable**
elements present (outfit, pose, setting, lighting) plus the trigger token —
never re-describing the immutable facial features (those should be implicit
in the trigger token / LoRA identity, not re-taught per image, which is what
causes prompt-caption fighting at inference time).

### What NOT to include (overfitting risks named explicitly)
- Any image where face angle is extreme enough that geometry is ambiguous
- Any 2 images that are near-duplicates (same pose/outfit/lighting, trivial
  variation) — dataset size should come from *variety*, not volume
- Any image where a single outfit/background/prop appears in more than
  ~20% of the set (risks being learned as identity)
- Any image with visible artifacts (extra fingers, warped jaw, asymmetric
  eyes, texture smearing) — training on flawed geometry teaches flawed geometry
- Any image where lighting makes skin tone read inconsistently with the rest
  of the set (confuses the identity's base skin tone)
- Any heavily stylized/filtered image (identity should be trained from
  "photographic" renders, not artsy edits)

### Per-image scoring rubric (0–10, keep if ≥ 7)
| Criterion | Points |
|---|---|
| Face clearly visible and unambiguous | 0–3 |
| Matches immutable trait list (no drift from canonical refs) | 0–3 |
| No visible AI artifacts (see QA checklist §7) | 0–2 |
| Adds variety not already covered by kept images (angle/light/outfit/bg) | 0–2 |

## 4. Canonical body reference

Alongside the facial identity pack, define once and keep fixed across all
versions: apparent height bracket, frame (e.g. "athletic, natural muscle
tone — not competition-level, not underweight"), shoulder/waist/hip
proportions in relative terms (not literal measurements — we're directing a
generator, not a tailor), and an explicit note: **fitness/lifestyle persona
means "visibly active", not hypersexualized or exaggerated by default.**
Any generation that noticeably changes body proportions from the canonical
reference fails QA regardless of how good the face looks.

## 5. Training strategy

**Method:** FLUX.1 LoRA, trained via `ai-toolkit` or `fluxgym` (both current,
actively maintained FLUX-LoRA trainers as of this research pass — re-verify
at Phase 4 execution time since tooling here moves fast).

| Hyperparameter | Value | Justification for *this* dataset (25–35 images, single character identity) |
|---|---|---|
| Rank | 32 | Small dataset + need to capture fine facial detail without excess capacity that overfits; 16 is common for style LoRAs but identity needs more capacity for geometry, 64 risks overfitting a 25–35 image set |
| Alpha | 16 (rank/2) | Standard scaling relationship, keeps effective learning rate stable at rank 32 |
| Resolution | 1024 | Matches dataset resolution and FLUX native training res |
| Repeats | 8–10 | With ~30 images this gives ~240–300 effective steps/epoch — enough signal per epoch without exploding total steps |
| Epochs | 10–15, checkpoint every epoch | Small dataset converges fast; checkpointing every epoch is what lets Phase 5 pick the best-generalizing checkpoint instead of assuming "last = best" |
| Learning rate | 1e-4 (UNet/transformer), 5e-5 (text encoder if trained) | Mid-range for LoRA rank 32 on a small dataset; higher risks overfitting fast given how few unique images there are |
| Optimizer | AdamW8bit | Standard for LoRA training, memory-efficient on rented consumer GPUs (24GB class) |
| Scheduler | cosine with warmup (~5% of steps) | Smooths convergence on a short run |
| Regularization | Light — a small class-image regularization set (generic "woman" images, not our character) at ~1:1 ratio if overfitting is observed in Phase 5; skip by default and only add if the consistency test shows over-fit symptoms (background/outfit bleeding into every output) | Regularization adds training cost/complexity; only justified reactively, not preemptively, on a dataset this small and this carefully curated |
| Validation | Generate from 5 held-out prompts (not seen in captions) every checkpoint, visually diffed against canonical refs | Cheap, catches drift before the formal Phase 5 test |
| Checkpoint selection | Best-scoring checkpoint on the Phase 5 Consistency Test, not automatically the final epoch | Later epochs on a small dataset commonly overfit texture/background before they finish learning geometry — must verify, not assume |

## 6. Character Consistency Test (Phase 5 gate)

Generate the character in these 15 conditions (per the brief's own list),
using the trained LoRA + PuLID stack + varied ControlNet pose refs:

1. selfie · 2. gym · 3. bikini/beach · 4. evening dress · 5. hoodie/casual ·
6. restaurant · 7. airport · 8. professional/campaign-style photo ·
9. night photo · 10. full body · 11. close-up · 12. profile ·
13. smiling · 14. serious/neutral expression · 15. hair tied back

### Identity Consistency Score (0–100)

```
Score = 0.40 × FaceEmbeddingScore
      + 0.20 × BodyProportionScore
      + 0.20 × DistinctiveFeatureScore
      + 0.20 × HumanReviewScore
```

- **FaceEmbeddingScore** — cosine similarity (InsightFace/ArcFace embeddings,
  `engine/identity/consistency_score.py`) between each of the 15 test images
  and the canonical frontal reference, averaged, normalized to 0–100. This is
  the objective, automatable core of the score.
- **BodyProportionScore** — manual/heuristic check that body proportions
  (§4) haven't drifted across full-body shots; start manual, automate later
  if a reliable pose/proportion estimator is added.
- **DistinctiveFeatureScore** — binary-per-image check that any fixed marks
  (specific mole/freckle pattern, if defined) are present and in the right
  place, since these are the strongest tell of identity leakage/drift.
- **HumanReviewScore** — you (or a second human) look at all 15 side-by-side
  with the canonical reference and rate "still obviously the same person":
  0/50/100 per image, averaged. Embeddings can be fooled by adversarial
  similarity in ways a human glance immediately catches — this term exists
  specifically as a check on the automated score, not a formality.

**Threshold: 80/100 to pass.** Below that, do not proceed to Phase 6 —
return to dataset (§3) or training (§5) and iterate. Document the failure
and the fix in `experiments/EXPERIMENT_LOG.md` so we don't re-try the same
failed configuration on influencer #2.

## 7. AI-Artifact QA checklist

Run on every image before it's eligible for approval (manually at first,
automated incrementally per Phase 7):

- [ ] Skin texture shows natural variation (pores, minor asymmetry) — not
      airbrushed/plastic
- [ ] Eyes: catchlights consistent with scene lighting, pupils same size,
      no glassy/dead look
- [ ] Teeth: countable, natural spacing/shape, no fusion or extra teeth
- [ ] Hair: strands resolve individually at the edges, no clumping into
      "plastic helmet" shapes, flyaways present where physically plausible
- [ ] Hands: 5 fingers, plausible joints, no fusion/extra digits
- [ ] Nails: present, plausible shape, consistent across visible hands
- [ ] Jewelry/earrings: symmetric where they should be, no melting into skin
- [ ] Clothing: seams/fabric behave physically, no melting into skin or
      other garments, text/logos (if any) are not garbled
- [ ] No garbled text anywhere in frame (signs, labels, screens)
- [ ] Reflections (mirrors, windows, sunglasses) are geometrically plausible
- [ ] Lighting direction/color consistent across the whole frame, shadows
      fall the correct direction
- [ ] Depth of field/perspective consistent with the stated camera/lens
      (no "everything in focus" when a shallow-DOF phone-portrait mode was
      requested, etc.)
- [ ] No excessive/uncanny symmetry in the face (a subtle natural asymmetry
      should be visible — perfect symmetry reads as synthetic)
- [ ] Background objects are coherent (no melted furniture, impossible
      architecture, duplicated people)
- [ ] Body proportions match the canonical body reference (§4)

An image failing **any** checked item is rejected, not "approved with a
note" — the checklist exists to keep the bar objective, not adjustable per
how much we like a particular shot.

## 8. Ethics & platform compliance

- The character is **fully original** — never generated by prompting
  "[real influencer name]" or by conditioning on a real person's photo. The
  zero-shot exploration phase (§2) generates *new* candidate faces from
  descriptive traits, not from any real individual's likeness.
- No deepfakes, no impersonation of any real, identifiable person.
- No use of private/third-party photos as face-conditioning input.
- Brand deals: the virtual nature of the influencer is disclosed to brand
  partners — no representing the character as a real person to a business
  counterparty.
- Platform disclosure: **Fanvue requires AI-generated accounts to be
  explicitly labeled during onboarding** (an "AI creator" badge is then
  applied automatically to the profile and all posts) — this is a hard
  requirement, not optional, and must be set correctly before any Fanvue
  content goes live (Phase 10 territory, re-verify current policy at that
  point since platform policy changes over time — see
  `docs/research/stack_research_2026.md`).
- Instagram/TikTok: check current AI-content labeling requirements
  immediately before Phase 9 (publishing) — do not assume today's research
  snapshot is still accurate months from now.
