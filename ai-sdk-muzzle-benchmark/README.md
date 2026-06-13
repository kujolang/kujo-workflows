# AI SDK + Muzzle Benchmark Workflow

This workflow benchmarks the same website-build prompt against the same model in two modes:

- `raw`: run the AI SDK request and verification commands directly.
- `muzzle`: run the noisy stages through Muzzle so the agent sees compact summaries while full logs stay on disk.

RunLedger records each attempt with model/provider metadata, token usage reported by the AI SDK, timing notes, changed files, and a final verdict.

## Quick Start

```bash
cd ai-sdk-muzzle-benchmark
bash scripts/run-benchmark.sh
```

Without provider keys, the workflow uses the AI SDK offline fixture and builds a deterministic local fixture app so the whole path still runs.

For a live OpenAI-compatible run:

```bash
OPENAI_API_KEY="..." PROVIDER=openai MODEL=gpt-4.1-mini bash scripts/run-benchmark.sh
```

For a stronger benchmark, run repeated paired trials. This defaults to `TEMPERATURE=0` to reduce model-output variance:

```bash
OPENAI_API_KEY="..." PROVIDER=openai MODEL=gpt-4.1-mini TRIALS=5 bash scripts/run-suite.sh
```

The suite runner creates one normal `.runs/<timestamp>-trial-XX/` folder per trial and one aggregate suite folder under `.suites/<timestamp>/`.

If a run shows `AI SDK ok: false`, `HTTP 404`, zero provider tokens, and `fixture` app source, the provider call did not produce model output. This benchmark currently uses the sibling AI SDK's `chat_completion` path, so choose a model available to that OpenAI-compatible chat endpoint or extend the AI SDK with a Responses API path before benchmarking Responses-only coding models.

DeepSeek and OpenRouter are also supported by the sibling AI SDK presets:

```bash
DEEPSEEK_API_KEY="..." PROVIDER=deepseek MODEL=deepseek-chat bash scripts/run-benchmark.sh
OPENROUTER_API_KEY="..." PROVIDER=openrouter MODEL=openai/gpt-4.1-mini bash scripts/run-benchmark.sh
```

## Outputs

Each run writes artifacts under:

```text
ai-sdk-muzzle-benchmark/.runs/<timestamp>/
  prompt.md
  summary.md
  compare.md
  review.html
  runledger/
  raw/
    ack.json
    app/
    logs/
    metrics.json
  muzzle/
    ack.json
    app/
    logs/
    metrics.json
  .muzzle/
    logs/
    reports/
```

Open `summary.md` first. `compare.md` gives the compact raw-vs-Muzzle table.
Open `review.html` for the shareable dashboard with charts, run cards, prompt modal, warning flags, and RunLedger excerpts.

Each suite writes artifacts under:

```text
ai-sdk-muzzle-benchmark/.suites/<timestamp>/
  review.html
  summary.md
  summary.json
  run-dirs.txt
  logs/
```

Open the suite `review.html` to see aggregate averages, standard deviation, min/max, per-trial links, success/fallback rate, provider-token deltas, local transcript savings, and timing deltas.

## Review Dashboard

Future benchmark runs generate `review.html` automatically. To regenerate it for an existing run:

```bash
node scripts/generate-review-html.js .runs/<timestamp>
```

The dashboard includes built-in pricing for `gpt-4.1-mini` using `$0.40 / 1M input tokens` and `$1.60 / 1M output tokens`. Optional cost estimates for other models can be added by passing per-million-token rates when generating the dashboard:

```bash
PRICE_INPUT_PER_MTOK=1.25 PRICE_OUTPUT_PER_MTOK=10 \
  node scripts/generate-review-html.js .runs/<timestamp>
```

The dashboard separates two different savings categories:

- Provider token usage: tokens reported by the AI SDK response. This should stay the same when the prompt and model are the same.
- Local transcript exposure: estimated tokens the agent sees from command output. This is where Muzzle should save context.

## Robust Suite Metrics

Use suite runs when you want evidence strong enough to talk about publicly:

```bash
OPENAI_API_KEY="..." PROVIDER=openai MODEL=gpt-4.1-mini TRIALS=10 TEMPERATURE=0 bash scripts/run-suite.sh
```

The suite report answers:

- Did both raw and Muzzle AI SDK calls succeed?
- Did both modes produce model-generated apps instead of fixture fallbacks?
- What was the average provider-token delta?
- What was the average local transcript/context reduction?
- How noisy were timing and output-token differences across runs?
- What is the estimated context-window cost saved if those local transcript tokens would otherwise be fed back into the agent?

Interpretation rule of thumb:

- If provider-token delta averages near zero, Muzzle is not changing the model prompt or model billing for the main request.
- If local transcript savings is large, Muzzle is helping preserve agent context and reducing compaction pressure during build/test/debug loops.

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `PROVIDER` | `openai` | AI SDK provider preset: `openai`, `deepseek`, or `openrouter`. |
| `MODEL` | provider default | Model to pass to the AI SDK. |
| `TRIALS` | `5` for suites | Number of paired raw/Muzzle trials for `run-suite.sh`. |
| `MAX_TOKENS` | `4000` | Completion budget for the app-generation request. |
| `TEMPERATURE` | `0.2` single run, `0` suite | Model temperature for live runs. |
| `KUJO_BIN` | sibling `../kujo/target/release/kujo` | Kujo runtime. |
| `KUJO_REPOS` | parent of this repo | Root folder containing sibling Kujo tools. |
| `PORT_BASE` | `8120` | Base port for local PHP verification. |
| `PRICE_INPUT_PER_MTOK` | model catalog when known | Optional dashboard-only input-token price per 1M tokens. |
| `PRICE_OUTPUT_PER_MTOK` | model catalog when known | Optional dashboard-only output-token price per 1M tokens. |

## What Muzzle Changes

Muzzle does not change the prompt sent to the model. It changes how noisy local stages are exposed to the agent:

- raw mode captures the full command output as the immediate transcript.
- muzzle mode captures full output in `.muzzle/logs/` and returns a short summary plus report paths.

That makes this workflow useful for comparing:

- provider token usage from the AI SDK response contract,
- wall-clock time for the model request and verification,
- local transcript bytes/tokens exposed to the agent,
- app verification outcomes,
- RunLedger receipts for repeated model comparisons.
