# Stack research — snapshot 2026-08-11

Findings backing the decisions in `ARCHITECTURE.md`. Re-verify before
relying on this for anything beyond the current phase — this field moves in
months, not years.

## Identity consistency methods

- **PuLID-Flux-II / InstantID-class adapters**: zero-shot identity injection
  from a single reference photo, no training. Fast to start, but drifts under
  large lighting/pose changes and can look "pasted on" when lighting doesn't
  match the reference. Best used for cheap exploration and as a secondary
  reinforcement signal, not as the sole identity mechanism for a long-lived
  character.
- **FLUX LoRA**: trained per-character, captures facial geometry *and*
  body-language/style cues a zero-shot adapter can't. Costs a dataset +
  training run, but becomes durable, reusable IP. Consensus across current
  guides: for a character meant to last (a brand mascot / recurring
  influencer), LoRA is superior to zero-shot-only.
- **2026 best-practice pattern observed**: lock a canonical face reference,
  build a small controlled "character sheet" (10–15+ clean crops from
  multiple angles/expressions against controlled backgrounds), train a LoRA
  on that sheet, then stack a zero-shot identity adapter (PuLID/Flux Kontext)
  on top per-generation for extra anchoring — this is exactly the hybrid
  approach adopted in `ARCHITECTURE.md` §2.2.
- Typical current FLUX LoRA hyperparameters observed across guides: rank
  16–64 for characters, alpha ≈ half of rank, learning rate 1e-4–5e-4,
  1000–3000 total training steps for a character LoRA. Our specific values
  in `IDENTITY_SYSTEM.md` §5 are chosen for our smaller, more tightly curated
  25–35 image dataset rather than copied wholesale.

Sources: [How to Create a Consistent AI Influencer in 2026](https://higgsfield.ai/blog/how-to-create-ai-influencer),
[How to Build a Consistent AI Character Across Images and Video](https://astorie.ai/blog/how-to-build-consistent-ai-character),
[PuLID Flux II in ComfyUI](https://www.runcomfy.com/comfyui-workflows/pulid-flux-ii-in-comfyui-consistent-character-ai-generation),
[Which way for Character Consistency?](https://heatherbcooper.substack.com/p/which-way-for-character-consistency),
[ComfyUI Consistent Character With FLUX (2026 Guide)](https://www.runflow.io/blog/comfyui-consistent-characters-flux),
[ComfyUI LoRA Training Guide 2026](https://www.apatero.com/blog/comfyui-lora-training-character-consistency-guide-2026).

## Cloud GPU pricing (observed, Aug 2026)

| Provider | Card | Price |
|---|---|---|
| RunPod | RTX 4090 | ~€0.32/hr |
| RunPod | A6000 (secure) | ~€0.33/hr |
| RunPod | A100-80GB (community) | ~€1.10/hr |
| RunPod | H100-80GB (community) | ~€1.85/hr |
| Thunder Compute | A100-80GB | ~€1.01/hr |
| fal.ai / Replicate | serverless, per-image | ~€0.02–0.04/image (model-dependent) |

RunPod offers the best reliability-to-price ratio for sustained training/batch
work; fal.ai/Replicate serverless removes idle cost entirely and is better
suited to low-volume/exploration use, which is exactly how we sequence them
by phase (`ARCHITECTURE.md` §2.4).

Sources: [Best Cloud GPU for AI Image Generation (Aug 2026)](https://www.thundercompute.com/blog/best-cloud-gpus-ai-art-generation),
[Best GPU for AI Training and Fine-Tuning in 2026](https://www.runpod.io/articles/guides/best-gpu-for-ai-training-2026),
[fal.ai vs Replicate GPU Cloud Pricing 2026](https://computeprices.com/compare/fal-ai-vs-replicate),
[fal.ai vs RunPod GPU Cloud Pricing 2026](https://computeprices.com/compare/fal-ai-vs-runpod).

## Apple Silicon 16GB local feasibility

- FLUX.1-dev "wants 24GB+ to run pleasantly" — confirms it should not run
  locally on our 16GB Mac.
- FLUX.2 klein (4B, ~7.75GB weights, fits ~13GB memory) and FLUX.1-Schnell at
  GGUF Q4 (~7GB) both fit comfortably on a 16GB Mac and are viable for local
  preview generation via MLX/MFLUX/Draw Things/ComfyUI.
- 16GB is described as "a solid sweet spot" for SD1.5/SDXL/lighter FLUX
  variants, ~10–40 sec/image depending on resolution — confirms local
  previews are practical, not just theoretically possible.
- Confirms the architecture split: local = lightweight/quantized preview
  models only, cloud = FLUX-dev production quality.

Sources: [MLX: Stable Diffusion for Local Image Generation on Apple Silicon](https://medium.com/@ingridwickstevens/mlx-stable-diffusion-for-local-image-generation-on-apple-silicon-2ec00ba1031a),
[Best AI Models for 16GB Mac](https://willitrunai.com/blog/best-ai-models-for-mac-16gb),
[How to use Flux AI model on Mac](https://stable-diffusion-art.com/flux-mac/).

## Fanvue AI-content policy (as of Aug 2026)

- Fanvue explicitly allows fully AI-generated personas/characters that are
  not real individuals, including AI content in permitted regions — currently
  one of the only major subscription platforms with an explicit, supported
  AI-creator path.
- Hard requirements: AI-generated media must not depict a real person other
  than the account owner, and must not resemble/imply anyone under 18.
- Disclosure is mandatory: creators must label the account as AI-generated
  during onboarding; once active, Fanvue applies an "AI creator" badge
  automatically and treats every post from that account as AI content.

This directly informs `IDENTITY_SYSTEM.md` §8 (Ethics & platform compliance)
and gates Phase 10 (monetization) — re-verify at that phase since policy can
change.

Sources: [Can You Use AI Models on Fanvue? (2026 Guide)](https://substy.ai/blog/can-you-use-ai-models-on-fanvue-whats-legal-whats-not-and-how-to-stay-safe-2026-guide),
[AI Generated Content | Fanvue Help Centre](https://help.fanvue.com/en/articles/8442803-ai-generated-content),
[AI Content Guidelines](https://www.fanvue.com/blog/ai-content-guidelines).
