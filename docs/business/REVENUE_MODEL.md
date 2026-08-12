# Revenue Model — Sofía

**Read this before the numbers:** every figure below is a modeled scenario
built from stated, labeled assumptions (typical creator-economy benchmarks),
not a guarantee, not a promise, and not validated by our own data yet. The
point of this document is to know **what would have to be true** to hit each
milestone, so we can check reality against it and correct fast — not to
present a forecast as fact. Replace assumptions with real numbers the moment
we have them (`experiments/EXPERIMENT_LOG.md` / `content/metrics/`), and
re-run this model quarterly at minimum.

## Revenue streams

| Stream | What it is | Time to first €1 | Notes |
|---|---|---|---|
| **Fanvue** — subscriptions | Monthly recurring, gated content | Slowest to meaningful volume, fastest to *first* euro once launched | Needs an existing audience funnel from Instagram/TikTok — don't launch Fanvue before there's traffic to send |
| **Fanvue** — PPV | Pay-per-view unlocks on top of subscription | Requires existing subscriber base | Higher ARPPU lever than subscription price alone |
| **Fanvue** — bundles / tips | Ad hoc | Low, unpredictable early | Upside only once there's an engaged base |
| **Brand deals** — posts/reels | Flat fee per sponsored post | Can land early even at small audience (nano-influencer tier) | Needs a credible, consistent feed (MVP §Launch sequencing) and honest AI-disclosure to brands (`IDENTITY_SYSTEM.md` §8) |
| **Brand deals** — UGC virtual / affiliate | Commission or flat fee for AI-generated "testimonial"-style content | Can start alongside posts/reels | Growing category specifically because AI creators can produce UGC-style content fast |
| **Affiliate marketing** | Commission on tracked links (fitness/beauty/travel products) | Can start Day 1, doesn't require brand outreach | Low per-conversion value, but zero negotiation overhead — good early cash-flow-positive test |
| **Digital products** | Own product (e.g. a workout/wellness guide under Sofía's brand) | Requires trust + audience first | Highest margin stream once viable — no per-unit generation cost |
| **Licensing / virtual model services** | Licensing Sofía's likeness/content to a brand or service | Requires proven, credible identity + portfolio | Speculative until the identity/content library is substantial |

## Unit economics

```
Contribution Margin = Revenue
                     − Cost of Generation (GPU/API, see COSTS.md)
                     − Tools/subscriptions
                     − Ads (if any)
                     − Platform fees/commissions
                     − Other direct costs
```

Track per channel, not just in aggregate — a channel with strong revenue but
thin margin isn't automatically the one to double down on.

| Metric | Definition | Why it matters here |
|---|---|---|
| CAC | Cost to acquire one paying subscriber/customer | Mostly organic at MVP stage → near-€0 CAC is the whole point of the funnel-from-social model; track separately if any paid promotion starts |
| ARPU | Average revenue per follower/user across the whole base | Sanity-checks "revenue per 1,000 followers" below |
| ARPPU | Average revenue per *paying* user | The number that actually drives Fanvue milestone math |
| LTV | Expected total revenue per paying subscriber over their lifetime | LTV must clear CAC + generation cost per subscriber by a healthy margin before scaling spend |
| Conversion rate | Followers → paying subscribers | The single highest-leverage unknown in this whole model — see assumptions below |
| Subscriber churn | % of subscribers lost per month | Directly sets sustainable subscriber count for a given monthly revenue target |
| Revenue / 1,000 followers | Cross-platform comparability metric | Lets us compare Instagram vs. TikTok funnel efficiency |
| Revenue / post | Total revenue attributable / posts published | Feeds back into "is more content actually worth producing" |
| Cost / approved image | From `COSTS.md` funnel | Ties content cost directly to the revenue side of the ledger |
| Cost / reel | Same, for video once Phase 11 exists | Not relevant until video phase |

## Working assumptions (label: ASSUMPTION — verify against real data)

- **ASSUMPTION A** — Instagram/TikTok organic follower growth for a
  consistent, well-executed niche fitness/lifestyle account: roughly
  500–3,000 followers/month in the first 3 months without paid promotion,
  highly variable, front-loaded by any single viral hit. This is a wide
  band on purpose — we don't have our own data yet.
- **ASSUMPTION B** — Social-to-Fanvue conversion rate (followers who ever
  subscribe): **0.5–2%** for a non-explicit fitness/lifestyle funnel. This
  is the single most important number in the whole model and the most
  likely to be wrong in either direction — instrument it from Day 1
  (`GO_TO_MARKET.md` Day 30–60).
- **ASSUMPTION C** — Fanvue subscription price: **€8–15/month** typical
  range for this content category; PPV/tips add roughly **30–60%** on top
  of subscription revenue for an active creator (wide range, unverified for us).
- **ASSUMPTION D** — Brand deal value at nano/micro tier: nano (10–50k
  followers) ≈ **€50–300/post**; micro (50–200k) ≈ **€300–1,500/post**;
  these are broad market benchmarks for human creators — a virtual creator
  may price lower until the format is more established, or command a
  premium for novelty/volume flexibility. Unverified for our niche specifically.
- **ASSUMPTION E** — Subscriber monthly churn: **10–20%**, typical for
  creator-subscription platforms without strong retention content —
  `GO_TO_MARKET.md` §RETENTION pillar exists specifically to fight this.

## Scenarios

Three scenarios per horizon — **Conservative** assumes the low end of every
assumption above and slower-than-hoped execution; **Base** assumes the
middle of each range with steady execution; **Aggressive** assumes the high
end plus at least one meaningful viral/brand-deal break. None of these are
promises.

### 30 days (still mostly pre-revenue — see `GO_TO_MARKET.md` Day 0–30)
| | Conservative | Base | Aggressive |
|---|---|---|---|
| Followers (combined) | 500 | 2,000 | 6,000 |
| Fanvue live? | No | Maybe (soft launch) | Yes |
| Revenue | €0 | €0–50 | €100–400 (early affiliate/small brand test) |

### 90 days
| | Conservative | Base | Aggressive |
|---|---|---|---|
| Followers (combined) | 2,000 | 8,000 | 25,000 |
| Fanvue subscribers | 5–10 | 30–60 | 150–300 |
| Fanvue revenue/mo | €50–100 | €300–700 | €1,500–3,500 |
| Brand/affiliate revenue/mo | €0 | €100–300 | €500–1,500 |
| **Total revenue/mo (month 3)** | **€50–100** | **€400–1,000** | **€2,000–5,000** |

### 6 months
| | Conservative | Base | Aggressive |
|---|---|---|---|
| Followers (combined) | 6,000 | 25,000 | 80,000 |
| Fanvue subscribers | 20–40 | 150–300 | 600–1,200 |
| **Total revenue/mo** | **€200–500** | **€1,500–3,500** | **€6,000–15,000** |

### 12 months
| | Conservative | Base | Aggressive |
|---|---|---|---|
| Followers (combined) | 15,000 | 60,000 | 200,000+ |
| Fanvue subscribers | 50–100 | 400–800 | 2,000+ |
| **Total revenue/mo** | **€500–1,200** | **€4,000–9,000** | **€20,000–40,000+** |

The **Base** column is the planning case for `COSTS.md` §Reinvestment
policy — not Aggressive. Reinvestment decisions should never be made against
the Aggressive column.

## Milestone reverse-engineering

Each milestone shows what has to be true, worked from Base-scenario
assumptions — not a claim it will happen by any specific date.

### First revenue (any amount)
- Cheapest realistic path: 1 affiliate conversion or 1 nano brand deal —
  needs only a credible feed (MVP, ~1,000+ followers) and zero subscriber base.
- Main risk: platform/brand willingness to work with a disclosed AI creator
  (mitigated by Fanvue's explicit AI-creator support, `IDENTITY_SYSTEM.md` §8;
  Instagram brand deals for AI creators are a newer, less proven category).

### Milestone 1 — €1,000/mo
- Example path: **~100 Fanvue subscribers × €10 ARPPU** = €1,000, at 1–2%
  conversion that's **5,000–10,000 relevant followers**; alternative/parallel
  path: 2–3 small brand deals/month (~€300–500 each) covers this without any
  subscriber base at all.
- Content volume: sustained posting per `WEEKLY_OPS.md` cadence, no
  additional infrastructure needed.
- Costs: still Stage 1 (`COSTS.md`, <€30/mo).
- Team: still just the current setup (owner + Claude).
- Influencers: 1 (Sofía).
- Main risks: conversion rate assumption (B) is the dominant lever here —
  if real conversion is 0.2% instead of 1%, this milestone needs 5x the
  followers.

### Milestone 2 — €3,000/mo
- Example path: **~250 subscribers × €10 ARPPU (€2,500)** + 1–2 brand
  deals/month (€500) ≈ €3,000; needs roughly **15,000–25,000 followers**
  at Assumption B conversion.
- Costs: likely into Stage 2 (`COSTS.md`, €30–100/mo) — more generation
  volume to sustain content cadence at a larger audience.
- Team: still solo, but production cadence (`WEEKLY_OPS.md`) becomes the
  real constraint — this is where automating QA (Phase 7) starts paying for itself.
- Influencers: still 1, unless the Multi-influencer trigger
  (`GO_TO_MARKET.md`) is already met.
- Main risks: churn (assumption E) — at 15-20% monthly churn, net-new
  subscriber acquisition has to outrun losses just to hold this number, not
  even grow it.

### Milestone 3 — €10,000/mo
- Example path: **~800 subscribers × €10 (€8,000)** + steady brand deal
  cadence (€2,000/mo, now at micro-tier pricing since audience has grown)
  ≈ €10,000; needs roughly **60,000–100,000 followers** at Assumption B.
- Costs: Stage 3 (`COSTS.md`, €100–300/mo) — daily batch generation,
  automated QA doing real work, likely first paid tooling for publishing automation.
- Team: still potentially solo with heavy automation, but this is the
  realistic zone to consider a part-time collaborator (content review,
  community management) — evaluate ROI before hiring, don't assume it's needed.
- Influencers: **Multi-influencer trigger should already be evaluated** —
  Sofía alone reaching this milestone is strong evidence for Influencer #2.
- Main risks: content-production ceiling (can generation/QA actually keep
  pace with a 60k+-follower audience's content appetite without quality
  dropping — this is exactly what Phase 7/8 automation exists to solve
  before it becomes a bottleneck).

### Milestone 4 — €30,000/mo
- Example path: this level realistically requires **multiple revenue
  streams compounding** — e.g. €15,000 Fanvue (1,200+ subscribers) +
  €10,000 brand deals (regular micro/mid-tier cadence) + €5,000
  affiliate/digital products; needs an audience in the **150,000–300,000**
  range at Base-scenario efficiency, or fewer followers at meaningfully
  better-than-assumed conversion/pricing.
- Costs: Stage 4 (`COSTS.md`, €300+/mo) — dedicated GPU capacity likely
  justified, real tooling investment.
- Team: likely needs at least one dedicated collaborator (content
  ops/community/brand outreach) — evaluate by ROI, not by milestone number alone.
- Influencers: 2–3 plausible by this point if Influencer #2/#3 were started
  around Milestone 3, sharing the same `engine/` (`ROADMAP.md` Phase 12).
- Main risks: this is well outside Base-scenario 12-month projections above
  — reaching it in year one would already be Aggressive-scenario territory;
  treat this milestone as a multi-year target unless early data strongly
  outperforms Base.

### Milestone 5 — €100,000/mo
- This is a **portfolio-of-influencers, small-studio outcome**, not a
  single-character outcome — realistically requires several influencers each
  performing near their own Milestone 3–4 level simultaneously, plus
  licensing/digital-product revenue that doesn't scale linearly with content cost.
- Not modeled in detail here because the assumptions that matter at this
  scale (team size, tooling, multi-influencer content economics) don't exist
  yet in our data — revisit this milestone once Milestone 3 is real, not before.
- Stated explicitly: **treat this as a long-term ambition, not a plan input.**

## Reinvestment policy

See `COSTS.md` §Reinvestment policy for the budget-stage rules this revenue
model feeds — stage transitions are gated on 2 consecutive months of revenue
clearing the stage's cost, using the **Base scenario**, never Aggressive.
