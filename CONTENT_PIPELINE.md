# Content Pipeline

Covers everything downstream of a validated identity (Phase 6+): the modular
prompt engine, the reusable photography-style and location libraries, the
clothing pipeline, the content engine, and the publishing workflow.

## 1. Prompt Engine (`engine/prompt_engine/`)

Never hand-write a full prompt from scratch. Prompts are assembled from
independent, swappable modules — implemented in
`engine/prompt_engine/modules.py`:

```
BASE IDENTITY   ← from identity_pack.yaml (immutable traits + trigger token)
SCENE           ← content type / activity / mood
OUTFIT          ← from clothing pipeline (§3) or identity_pack "usual" defaults
POSE            ← text description + optional ControlNet reference image
CAMERA          ← from photo style library (§2)
LIGHTING        ← from photo style library (§2)
REALISM         ← fixed boilerplate fragment: film grain / natural skin texture
                  / phone sensor characteristics — tuned once, reused everywhere
NEGATIVE        ← fixed "avoid" fragment: plastic skin, extra fingers, warped
                  anatomy, text artifacts, etc. — mirrors the QA checklist so
                  we're steering away from exactly what QA checks for
IDENTITY CONTROL← LoRA reference + PuLID reference image + weight settings
```

`build_prompt(identity_pack, scene, outfit, pose, style, location)` composes
these into the final prompt bundle (positive prompt, negative prompt,
ControlNet refs, LoRA/PuLID settings) — a pure function, fully unit-testable
without any GPU (see `tests/test_prompt_engine.py`).

## 2. Photography style library (`engine/styles/photo_styles.yaml`)

Each style is a reusable bundle of camera/lens/lighting/imperfection
parameters, so "make it look like an iPhone selfie" is one config lookup, not
a re-invented prompt every time:

| Style | Camera/lens | Framing | Light | Imperfections |
|---|---|---|---|---|
| iphone_selfie | phone front camera, wide, slight barrel distortion | close, arm's-length | available light, sometimes flash-lit | mild noise, slight motion blur ok |
| mirror_selfie | phone rear camera reflected | half/full body, phone visible in reflection | bathroom/gym ambient | reflection imperfections, slight tilt |
| gym_photo | phone camera, casual angle | half body, mid-activity | harsh gym fluorescent/mixed | sweat sheen, motion blur on limbs ok |
| boyfriend_pov | phone camera, candid framing | full/half body, subject looking away or mid-laugh | natural outdoor/indoor | imperfect framing, not centered |
| professional_campaign | DSLR/mirrorless look, 50–85mm equiv, shallow DOF | controlled studio or styled location | soft key + fill, controlled | minimal — this is the one "clean" style |
| paparazzi | telephoto compression, slight grain | candid, mid-motion | mixed/harsh available light | motion blur, slight out-of-focus ok |
| nightlife | phone/low-light compact | close-mid, flash-lit | direct flash + ambient neon/bar light | flash noise, red-eye risk (avoid), slight blur |
| restaurant | phone camera, table-level | half body/table context | warm indoor ambient | mild noise |
| travel | phone/compact, wide landscape context | full body in environment | golden hour/daylight | dust/haze ok, natural |
| beach | phone camera, bright daylight | full/half body | strong sun, hard shadows | water droplets, wind-blown hair ok |
| home_morning | phone camera, casual | close/half body | soft window light | unstyled hair ok, cozy imperfect framing |
| story_photo | phone camera, vertical, casual | any | whatever's ambient | text/sticker overlay implied, low production value on purpose |

Each entry in the YAML expands to concrete prompt fragments (lens
characteristics, grain amount, motion-blur toggle, DOF) consumed by the
CAMERA/LIGHTING/REALISM prompt modules above. This library is what gives
"variety without losing identity" (brief §13) — identity conditioning stays
fixed while only this module swaps.

## 3. Clothing pipeline

Stage 1–5 approach (kept deliberately simple): **text description + IP-Adapter
garment-reference image**, applied to the OUTFIT prompt module, optionally
combined with inpainting when swapping an outfit on an otherwise-approved
image. This covers "generate her wearing something close to this reference
photo/product shot" — the brand-deal use case — without the added complexity
of a full virtual try-on model.

**Deferred to Phase 6 evaluation, not decided now:** dedicated garment-warping
try-on models (e.g. CatVTON/OOTDiffusion-class) — only worth the added
pipeline complexity if text+IP-Adapter garment fidelity proves insufficient
for real brand-deal accuracy requirements. Re-assess with real examples at
that point rather than pre-building it speculatively.

## 4. Location library (`engine/locations/locations.yaml`)

Each location entry defines the visual descriptors needed for coherent
background generation: architecture style, characteristic color palette,
typical vegetation/light quality, recognizable environmental cues (without
copyrighted landmark close-ups where avoidable) — e.g. Barcelona (Mediterranean
light, mixed modernist/narrow-street architecture, terracotta tones) vs. Bali
(tropical, dense greenery, warm golden light) vs. NYC (dense vertical
skyline, yellow cabs, cooler light). The rule from the brief holds: if a post
says "Barcelona", the background must read as Barcelona, not a generic
placeholder — this library is what keeps that coherent across many
generations instead of relying on remembering it per-prompt. Combined with
ControlNet composition control (`ARCHITECTURE.md` §2.3) for shots that need
to reference a specific real photo's framing without copying its people.

## 5. Content Engine (Phase 8)

```
input:  influencer + content_type + location + outfit + activity + mood
   ↓
concept → prompt (via Prompt Engine, §1) → generation (batch of 4–8)
   ↓
variant selection (automated pre-filter, Phase 7, + human final pick)
   ↓
QA (AI-Artifact checklist + Identity Consistency spot-check)
   ↓
retouch (only if a minor, targeted fix — not a crutch for bad generations)
   ↓
upscale (local Real-ESRGAN)
   ↓
metadata (tags: content_type, location, outfit, mood, generation config,
cost — feeds `content/metrics/` and `experiments/EXPERIMENT_LOG.md`)
   ↓
caption (from Personality Bible tone/voice, drafted per post)
```

Minimizing manual work means minimizing manual *prompt writing and repeated
QA judgment calls*, not skipping QA itself — the QA gate stays a hard
requirement per `IDENTITY_SYSTEM.md`.

## 6. Content calendar (Phase 8/9)

A believable Instagram/TikTok presence is not 30 professional photoshoots a
month — it's a deliberate mix, generated in batches by content type:

- Premium/campaign-style content: low frequency (weekly-ish), highest QA bar
- Everyday/lifestyle content: higher frequency, the "casual iPhone photo"
  styles from §2 dominate here
- Stories/casual: highest frequency, lowest production polish (by design —
  matches the `story_photo` style)
- Themed content (fitness, travel, food, outfits, collabs): planned in
  batches per location/trip rather than one-off, for narrative coherence
  (e.g. a "Bali trip" batch generated together, posted over several days)

The calendar is a data structure (`content/calendar/`), not a UI, at this
stage — a simple dated list of planned content-engine inputs.

## 7. Publishing workflow (Phase 9 — not built yet)

Deferred until Phase 9. Will need: Instagram/TikTok creator account access
(external account decision — yours), current platform AI-disclosure policy
re-verified at that time, and a decision on manual vs. API-based publishing
depending on account type and API access tier available then. Not designed
in detail now because platform APIs and policies are exactly the kind of
thing that goes stale between Phase 0 and Phase 9.
