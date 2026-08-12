# Go-To-Market Plan — Sofía

Runs **in parallel** with the technical pipeline, not after it. Owner:
Claude, per `CLAUDE.md` — kept current as decisions/data land, not written
once and abandoned. See `REVENUE_MODEL.md` for the money model this plan
feeds, and `WEEKLY_OPS.md` for the recurring execution rhythm this plan
hands off to after Day 30.

## MVP — what "launched" actually requires

Everything else is explicitly **SHOULD HAVE AFTER VALIDATION** or
**SCALE LATER** (`CLAUDE.md` §5) until these ten are true:

| # | MUST HAVE BEFORE LAUNCH | Status source |
|---|---|---|
| 1 | Excellent canonical identity (one locked face, chosen from real candidates, not just described) | `IDENTITY_SYSTEM.md` §2, Phase 2 |
| 2 | Sufficient facial consistency (Identity Consistency Score ≥ 80) | `IDENTITY_SYSTEM.md` §6, Phase 5 gate |
| 3 | Sufficient body consistency (canonical body reference holds across shots) | `IDENTITY_SYSTEM.md` §4 |
| 4 | Reproducible pipeline (prompt engine + styles/locations wired, not one-off hand-crafted images) | `CONTENT_PIPELINE.md`, Phase 6 |
| 5 | 20–40 publishable images (passed AI-Artifact QA + identity score) | Phase 6 output |
| 6 | Initial content library covering the launch sequence below (§Launch sequencing) | this doc |
| 7 | Social profiles set up (Instagram + TikTok, bio, AI-disclosure where required) | Phase 9, pulled forward for account creation only |
| 8 | Publishing strategy (what goes out, in what order — §Launch sequencing) | this doc |
| 9 | Launch calendar (Day 0–30 schedule, below) | this doc |
| 10 | Basic system to learn from metrics (even a manual spreadsheet counts at MVP stage) | `WEEKLY_OPS.md` §Measure |

Items 1–5 are technical and gated by `IDENTITY_SYSTEM.md` — never shipped
early. Items 6–10 are this document, and can be *designed* now even before
1–5 are done, so launch happens the moment the technical gate clears instead
of starting the commercial design afterward.

## Day-by-day plan

### Day 0 — Foundation (parallel with Phase 2–5 technical work)
- **Objective:** everything non-visual ready so publishing can start the
  instant the identity gate passes.
- **Assets needed:** Instagram + TikTok handles reserved, bio copy drafted
  (from `personality_bible.yaml`), AI-disclosure language prepared per
  current platform policy (re-verify at execution time, `IDENTITY_SYSTEM.md` §8).
- **Content:** none published yet.
- **Platforms:** Instagram (primary), TikTok (secondary, same content
  repurposed).
- **Experiments:** none yet.
- **KPI:** N/A — readiness checklist only.
- **Continue/change:** proceed once handles are secured and identity gate
  (Phase 5) is on track.
- 🔒 Requires creating the Instagram/TikTok accounts — external account,
  flagged per `CLAUDE.md` §3, not created without sign-off.

### Day 0–7 — Feed pre-loading (no public posting yet)
- **Objective:** the profile must not look like an empty new account the
  moment it goes public — pre-build a feed that already tells a story.
- **Assets:** 20–40 approved images from Phase 6, organized into the content
  pillars below.
- **Content:** build out the **first 9–12 grid posts** before the account is
  ever made public/discoverable — enough for a visitor's first impression to
  read as "established, real person," not "brand new." Mix across pillars
  (see §Content pillars) rather than 12 gym selfies in a row.
- **Platforms:** Instagram grid staged (private or unlisted where the
  platform allows), TikTok drafts prepared.
- **Experiments:** none — this week is production, not testing.
- **KPI:** 9–12 posts ready, each passing QA + identity score.
- **Continue/change kill criterion:** if fewer than 9 images from the batch
  pass QA, the funnel problem gets diagnosed (`COSTS.md` acceptance-rate
  metric) before more images are generated blindly.

### Day 7–14 — Soft launch
- **Objective:** go public, no paid/aggressive growth push yet — establish
  baseline organic signal.
- **Content:** publish the pre-loaded grid (§Day 0–7) on a realistic
  cadence (not all 12 at once — spread over the week to look like an
  existing posting rhythm), start daily/near-daily Stories.
- **Platforms:** Instagram live, TikTok first 3–5 posts (repurposed +
  TikTok-native cuts).
- **Frequency:** Instagram 1 feed post/day, Stories most days; TikTok 3–5
  for the week.
- **Experiments:** none yet — first week of real data collection only.
- **KPI:** baseline established for reach, follow-through rate (profile
  visits → follows), saves, comments — whatever the platforms report,
  logged in `content/metrics/`.
- **Continue/change:** if the account gets flagged/restricted (platform
  policy risk), stop and treat as a real blocker (`CLAUDE.md` §3.6) — don't
  push through it.

### Day 14–30 — First growth experiments
- **Objective:** find which content pillar/format actually earns reach, with
  real hypotheses, not more "pretty content."
- **Content:** 2–3 explicit format hypotheses running in parallel (see
  §Virality hypotheses below for the format).
- **Frequency:** ramp toward sustainable cadence discovered from Week 2 data
  — don't force a number, follow what the acceptance-rate/production
  capacity actually supports.
- **Experiments:** each hypothesis gets a success + kill criterion
  (`CLAUDE.md` §7) logged before publishing, evaluated after enough data
  (rule of thumb: ≥5 posts per format before judging, fewer than that is noise).
- **KPI:** engagement rate by pillar/format, follower growth rate,
  reach-per-post trend.
- **Continue/change:** kill formats that underperform after 5 tries across 2
  consecutive weeks; double down on whatever's winning.

### Day 30–60 — Monetization groundwork
- **Objective:** start the funnel toward revenue without forcing it before
  there's an audience to convert.
- **Content:** introduce trust-building content (behind-the-scenes-style,
  more personal voice per `personality_bible.yaml`) and the first soft CTA
  toward a secondary platform (Fanvue) if audience size/engagement supports
  it — see `REVENUE_MODEL.md` for the funnel logic and the actual gating
  metric, not a fixed date.
- **Experiments:** caption CTA styles, link-in-bio structure, posting time
  optimization.
- **KPI:** click-through on bio link, early Fanvue signups if launched,
  DM/comment sentiment as a trust proxy.
- 🔒 Fanvue account creation + AI-disclosure onboarding is an external
  account decision — flagged, not created unilaterally.

### Day 60–90 — Consolidate and decide on scale
- **Objective:** have enough signal to make the Influencer #2 decision
  (§Multi-influencer trigger) and a real (if early) revenue number.
- **Content:** double down on the 1–2 best-performing pillars/formats from
  Day 14–60 data; retire what's been killed.
- **Experiments:** first brand-deal outreach test (small/nano scale) if
  audience size makes it credible.
- **KPI:** the full North Star set in `WEEKLY_OPS.md` §North Star Metrics —
  by Day 90 there should be a real trend line, not just Day-1 numbers.
- **Continue/change:** this is the checkpoint for the reinvestment decision
  in `COSTS.md` §Reinvestment policy and the Influencer #2 go/no-go below.

## Launch sequencing (what the grid needs to say, in order)

A brand-new account with zero narrative reads as fake even with perfect
images. The first 9–12 posts are sequenced, not random:

1. **Introduction beat** (1–2 posts) — an approachable, high-identity-fidelity
   shot that reads as "this is who I am" (professional_campaign or clean
   iphone_selfie style, `CONTENT_PIPELINE.md` §2)
2. **Lifestyle proof** (3–4 posts) — gym, home_morning, restaurant styles —
   establishes the fitness+lifestyle premise with variety, not repetition
3. **Personality beat** (2 posts) — a candid/story-style shot with caption
   voice doing real work (`personality_bible.yaml` tone)
4. **Aspirational beat** (2–3 posts) — travel/beach style — the "this is a
   life worth following" signal
5. **Trust beat** (1 post) — something a bot/spam account would never post:
   a slightly imperfect, very candid shot — signals authenticity precisely
   because it's not polished

## Content pillars (every piece gets tagged, not just "pretty content")

| Pillar | Purpose | Typical styles |
|---|---|---|
| **REACH** | Get shown to non-followers | short-form video hooks, trending formats once Virality Engine data exists |
| **ENGAGEMENT** | Get comments/saves/shares from existing followers | relatable captions, questions, POV formats |
| **TRUST** | Feel like a real, consistent person | candid/imperfect shots, behind-the-scenes tone, consistent voice |
| **CONVERSION** | Move someone toward Fanvue/brand link | soft CTAs, premium-feeling content, bio-link-driven captions |
| **RETENTION** | Keep existing followers/subscribers around | consistency of posting, inside-joke/callback captions, recurring locations/routines from `personality_bible.yaml` |

Every content-calendar entry (`content/calendar/`) gets tagged with its
primary pillar so performance can be analyzed by pillar, not just overall.

## Virality hypotheses (format, not vibes)

Work like this, always: **hypothesis → create → publish → measure → compare
→ keep/kill.** Example starting hypotheses for Day 14–30 (replace with
real current-trend research at execution time — see §Competitive benchmarking):

- H1: "POV-style fitness reels of 7–12s get higher completion rate than 20s+ montage reels."
- H2: "Mirror-selfie style posts outperform professional_campaign style on saves (trust signal)."
- H3: "Captions with a direct question get more comments than statement captions."

Each hypothesis needs ≥5 posts before judging (statistical noise floor at
launch-stage follower counts) and an explicit kill criterion set *before*
publishing, not decided after seeing results (that's just confirmation bias).

## Competitive benchmarking (method, not identity copying)

Before Day 14 experiments, pull patterns (not content, not identities) from:
human fitness/lifestyle creators, existing virtual/AI influencers, and
general lifestyle creators — specifically: hook structures, posting
frequency, caption length/style, format mix, and (where visible) funnel
structure toward monetization. Convert every observation into one of our own
testable hypotheses (§above) — never copy a specific post or identity.

## Multi-influencer trigger (Influencer #2 go/no-go)

Do not start Influencer #2 until **all** of these hold for Sofía
(`ROADMAP.md` Phase 12 precondition, restated here as the business trigger):
- Consistent content production (acceptance rate stable, not still being debugged)
- Reliable pipeline (Phase 6+ running without hand-holding per generation)
- Real growth signal (positive trend over ≥4 consecutive weeks, not one viral fluke)
- First actual conversions (Fanvue signups or a brand deal, not just interest)

When those hold, use `ROADMAP.md` Phase 12's reproducibility DoD (new
influencer reaches its own Phase 5 gate using existing `engine/` tooling,
zero engine code changes) as the technical readiness check, and
`REVENUE_MODEL.md`'s reinvestment milestones as the financial readiness check.
