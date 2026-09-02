# AI SDK + Watchdog Showcase Workflow

This workflow shows why Watchdog is useful by running AI Chat-style requests through the Kujo AI SDK and Watchdog's OpenAI-compatible proxy.

It uses `../ai-chat/bridge_chat.kujo` as the example app boundary, `../ai-sdk/src` as the provider-normalization layer, and `../watchdog` as the telemetry proxy/dashboard.

The workflow is self-contained by default: it starts a tiny local OpenAI-compatible fixture upstream, so no live provider key is required.

## Quick Start

```bash
cd ai-sdk-watchdog-showcase
bash scripts/run-showcase.sh
```

The runner starts:

- a fixture OpenAI-compatible upstream on `UPSTREAM_PORT` (default `8781`)
- Watchdog on `WATCHDOG_PORT` (default `8780`)
- three AI Chat bridge calls routed to `http://127.0.0.1:${WATCHDOG_PORT}/proxy/v1`

For a live OpenAI run:

```bash
OPENAI_API_KEY="sk-..." USE_LIVE_OPENAI=1 bash scripts/run-showcase.sh
```

Live mode skips the fixture upstream and points Watchdog at `https://api.openai.com/v1`. It sends two real OpenAI chat-completion requests by default. Those calls may incur provider cost. The API key is passed to Watchdog via environment variable and is not written to `run-meta.json`.

## Outputs

Each run writes a packet under:

```text
ai-sdk-watchdog-showcase/.runs/<timestamp>/
  summary.md
  ai-chat/
    response-01.json
    response-02.json
    response-03.json      # fixture mode, or live mode with INCLUDE_ERROR_CASE=1
  watchdog/
    stats.json
    requests.json
    tool-calls.json
    agent-steps.json
    status-breakdown.json
    export.json
    telemetry-v2-records.json
    telemetry-v2.jsonl
    export-status.json
  logs/
    mock-upstream.log
    watchdog.log
```

Open `summary.md` first. It answers:

- Did AI Chat's bridge successfully use the AI SDK through Watchdog?
- Which requests succeeded or failed?
- What did Watchdog capture: requests, tool calls, agent steps, latency, usage, cost, and errors?
- Where are the raw telemetry exports for review?

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `KUJO_REPOS` | parent of this repo | Folder containing sibling `kujo`, `ai-sdk`, `ai-chat`, and `watchdog` repos. |
| `KUJO_BIN` | `$KUJO_REPOS/kujo/target/release/kujo` | Kujo runtime. |
| `AI_SDK_PATH` | `$KUJO_REPOS/ai-sdk/src` | Directory with `ai_sdk.kujo` and `providers.kujo`. |
| `AI_CHAT_DIR` | `$KUJO_REPOS/ai-chat` | Example app repo containing `bridge_chat.kujo`. |
| `WATCHDOG_DIR` | `$KUJO_REPOS/watchdog` | Watchdog repo containing `dashboard_server.kujo`. |
| `WATCHDOG_PORT` | `8780` | Local Watchdog dashboard/proxy port. |
| `UPSTREAM_PORT` | `8781` | Local fixture OpenAI-compatible upstream port. |
| `USE_LIVE_OPENAI` | `0` | Set to `1` to route Watchdog to the real OpenAI API instead of the fixture upstream. |
| `OPENAI_API_KEY` | empty | Required when `USE_LIVE_OPENAI=1`; passed to Watchdog as its upstream override key. |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Model used in fixture and live OpenAI requests. |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible upstream base URL for live mode. |
| `INCLUDE_ERROR_CASE` | fixture: `1`, live: `0` | Include a third provider-error request. In live mode this uses an intentionally invalid model and should be opt-in. |
| `RUN_DIR` | `.runs/<timestamp>` | Output packet directory. |

## What This Demonstrates

Without Watchdog, the app gets only the normalized AI SDK response. With Watchdog in the middle, the same app flow also produces reviewable telemetry:

- request status and latency
- normalized model and token usage
- cost estimate
- metadata-only canonical trace/span/event records
- provider errors
- proxy lifecycle agent steps
- proxy forward tool-call records
- JSON export for dashboards, tests, and regression checks
- versioned, replayable JSONL v2 and isolated exporter status

Content capture remains off by default. The workflow does not enable prompt,
response, tool input/output, retrieval, shell, or error-detail capture. The
legacy request views are retained as compatibility evidence; the canonical v2
record API and JSONL stream are the interoperability proof.

## Live Provider Variant

The default fixture upstream is intentional for repeatable demos. Live OpenAI mode is useful when you want Watchdog evidence from real provider traffic:

```bash
OPENAI_API_KEY="sk-..." \
USE_LIVE_OPENAI=1 \
OPENAI_MODEL="gpt-4.1-mini" \
bash scripts/run-showcase.sh
```

If you also want a live provider-error row in Watchdog, opt in explicitly:

```bash
OPENAI_API_KEY="sk-..." \
USE_LIVE_OPENAI=1 \
INCLUDE_ERROR_CASE=1 \
bash scripts/run-showcase.sh
```

That third call intentionally uses an invalid model name so Watchdog can capture an upstream failure. Keep it off for normal live demos.
