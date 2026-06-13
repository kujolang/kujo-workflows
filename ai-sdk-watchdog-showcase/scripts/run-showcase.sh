#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$ROOT/../.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
AI_SDK_PATH="${AI_SDK_PATH:-$KUJO_REPOS/ai-sdk/src}"
AI_CHAT_DIR="${AI_CHAT_DIR:-$KUJO_REPOS/ai-chat}"
WATCHDOG_DIR="${WATCHDOG_DIR:-$KUJO_REPOS/watchdog}"

WATCHDOG_PORT="${WATCHDOG_PORT:-8780}"
UPSTREAM_PORT="${UPSTREAM_PORT:-8781}"
USE_LIVE_OPENAI="${USE_LIVE_OPENAI:-0}"
OPENAI_MODEL="${OPENAI_MODEL:-gpt-4.1-mini}"
OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.openai.com/v1}"
INCLUDE_ERROR_CASE="${INCLUDE_ERROR_CASE:-}"
STAMP="${STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="${RUN_DIR:-$ROOT/.runs/$STAMP}"
LOG_DIR="$RUN_DIR/logs"
AI_CHAT_OUT="$RUN_DIR/ai-chat"
WATCHDOG_OUT="$RUN_DIR/watchdog"

WATCHDOG_URL="http://127.0.0.1:$WATCHDOG_PORT"
WATCHDOG_PROXY_URL="$WATCHDOG_URL/proxy/v1"
UPSTREAM_URL="http://127.0.0.1:$UPSTREAM_PORT"
UPSTREAM_BASE_URL="$UPSTREAM_URL/v1"
UPSTREAM_MODE="fixture"
UPSTREAM_API_KEY="fixture-upstream-key"

if [ "$USE_LIVE_OPENAI" = "1" ] || [ "$USE_LIVE_OPENAI" = "true" ]; then
	if [ -z "${OPENAI_API_KEY:-}" ]; then
		echo "USE_LIVE_OPENAI=1 requires OPENAI_API_KEY." >&2
		exit 1
	fi
	UPSTREAM_MODE="openai"
	UPSTREAM_URL="https://api.openai.com"
	UPSTREAM_BASE_URL="$OPENAI_BASE_URL"
	UPSTREAM_API_KEY="$OPENAI_API_KEY"
fi

if [ -z "$INCLUDE_ERROR_CASE" ]; then
	if [ "$UPSTREAM_MODE" = "fixture" ]; then
		INCLUDE_ERROR_CASE="1"
	else
		INCLUDE_ERROR_CASE="0"
	fi
fi

mkdir -p "$LOG_DIR" "$AI_CHAT_OUT" "$WATCHDOG_OUT"

MOCK_PID=""
WATCHDOG_PID=""
STARTED_MOCK="0"
STARTED_WATCHDOG="0"

port_in_use() {
	local port="$1"
	lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

kill_port_listener() {
	local port="$1"
	local pids
	pids="$(lsof -nP -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
	if [ -n "$pids" ]; then
		kill $pids >/dev/null 2>&1 || true
		sleep 0.2
		pids="$(lsof -nP -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
		if [ -n "$pids" ]; then
			kill -9 $pids >/dev/null 2>&1 || true
		fi
	fi
}

cleanup() {
	local code=$?
	if [ -n "$WATCHDOG_PID" ] && kill -0 "$WATCHDOG_PID" >/dev/null 2>&1; then
		kill "$WATCHDOG_PID" >/dev/null 2>&1 || true
		wait "$WATCHDOG_PID" >/dev/null 2>&1 || true
	fi
	if [ "$STARTED_WATCHDOG" = "1" ]; then
		kill_port_listener "$WATCHDOG_PORT"
	fi
	if [ -n "$MOCK_PID" ] && kill -0 "$MOCK_PID" >/dev/null 2>&1; then
		kill "$MOCK_PID" >/dev/null 2>&1 || true
		wait "$MOCK_PID" >/dev/null 2>&1 || true
	fi
	if [ "$STARTED_MOCK" = "1" ]; then
		kill_port_listener "$UPSTREAM_PORT"
	fi
	exit "$code"
}
trap cleanup EXIT INT TERM

require_path() {
	local kind="$1"
	local target="$2"
	if [ ! -e "$target" ]; then
		echo "$kind not found: $target" >&2
		exit 1
	fi
}

wait_for_json() {
	local url="$1"
	local label="$2"
	local attempts="${3:-80}"
	local i=1
	while [ "$i" -le "$attempts" ]; do
		if curl -fsS "$url" >/dev/null 2>&1; then
			return 0
		fi
		sleep 0.25
		i=$((i + 1))
	done
	echo "Timed out waiting for $label at $url" >&2
	return 1
}

bridge_payload() {
	local prompt="$1"
	local max_retries="$2"
	local model="$3"
	node -e '
const [baseUrl, prompt, maxRetries, model] = process.argv.slice(1);
process.stdout.write(JSON.stringify({
  provider_id: "custom",
  base_url: baseUrl,
  api_key: "ai-chat-profile-key",
  model,
  temperature: 0.2,
  max_tokens: 500,
  max_retries: Number(maxRetries),
  retry_delay_ms: 100,
  messages: [
    { role: "system", content: "You are the AI Chat showcase assistant. Keep answers concise and operational." },
    { role: "user", content: prompt }
  ]
}));
' "$WATCHDOG_PROXY_URL" "$prompt" "$max_retries" "$model"
}

run_bridge_call() {
	local index="$1"
	local prompt="$2"
	local max_retries="$3"
	local model="${4:-$OPENAI_MODEL}"
	local out="$AI_CHAT_OUT/response-$index.json"
	local raw="$AI_CHAT_OUT/response-$index.raw.log"
	local payload
	payload="$(bridge_payload "$prompt" "$max_retries" "$model")"

	(
		cd "$AI_SDK_PATH"
		KUJO_AI_SDK_ALLOW_INSECURE_LOCALHOST=1 \
			CUSTOM_API_KEY="ai-chat-profile-key" \
			"$KUJO_BIN" run "$AI_CHAT_DIR/bridge_chat.kujo" --interpreter -- --payload "$payload"
	) >"$raw" 2>"$AI_CHAT_OUT/response-$index.stderr.log" || true

	node -e '
const fs = require("fs");
const rawPath = process.argv[1];
const outPath = process.argv[2];
const raw = fs.readFileSync(rawPath, "utf8").trim();
const lines = raw.split(/\r?\n/).filter(Boolean);
let parsed = null;
for (let i = lines.length - 1; i >= 0; i -= 1) {
  try {
    parsed = JSON.parse(lines[i]);
    break;
  } catch {}
}
if (!parsed) {
  parsed = { ok: false, error: { code: "bridge_parse_failed", message: raw || "empty bridge output" } };
}
fs.writeFileSync(outPath, `${JSON.stringify(parsed, null, 2)}\n`);
' "$raw" "$out"
}

fetch_watchdog() {
	local path="$1"
	local out="$2"
	curl -fsS "$WATCHDOG_URL$path" > "$out"
}

require_path "Kujo runtime" "$KUJO_BIN"
require_path "AI SDK path" "$AI_SDK_PATH/ai_sdk.kujo"
require_path "AI Chat bridge" "$AI_CHAT_DIR/bridge_chat.kujo"
require_path "Watchdog server" "$WATCHDOG_DIR/dashboard_server.kujo"

if port_in_use "$WATCHDOG_PORT"; then
	echo "Watchdog port $WATCHDOG_PORT is already in use. Set WATCHDOG_PORT to a free port or stop the existing listener." >&2
	exit 1
fi

if [ "$UPSTREAM_MODE" = "fixture" ] && port_in_use "$UPSTREAM_PORT"; then
	echo "Fixture upstream port $UPSTREAM_PORT is already in use. Set UPSTREAM_PORT to a free port or stop the existing listener." >&2
	exit 1
fi

if [ "$UPSTREAM_MODE" = "fixture" ]; then
	node "$ROOT/scripts/mock-openai-server.js" --port "$UPSTREAM_PORT" >"$LOG_DIR/mock-upstream.log" 2>&1 &
	MOCK_PID="$!"
	STARTED_MOCK="1"
	wait_for_json "$UPSTREAM_URL/healthz" "fixture upstream"
else
	printf 'live OpenAI mode enabled; fixture upstream not started\n' >"$LOG_DIR/mock-upstream.log"
fi

(
	cd "$WATCHDOG_DIR"
	WDG_PORT="$WATCHDOG_PORT" \
		WDG_DB_PATH="$RUN_DIR/watchdog.db" \
		WDG_PROXY_CONFIG_PATH="$RUN_DIR/watchdog_proxy_config.json" \
		WDG_UPSTREAM_BASE_URL="$UPSTREAM_BASE_URL" \
		WDG_PROXY_AUTH_MODE="override" \
		WDG_UPSTREAM_API_KEY="$UPSTREAM_API_KEY" \
		WDG_REDACTION_MODE="basic" \
		"$KUJO_BIN" run --interpreter dashboard_server.kujo
) >"$LOG_DIR/watchdog.log" 2>&1 &
WATCHDOG_PID="$!"
STARTED_WATCHDOG="1"
wait_for_json "$WATCHDOG_URL/healthz" "Watchdog"
wait_for_json "$WATCHDOG_URL/api/proxy-config" "Watchdog proxy config"

cat > "$RUN_DIR/run-meta.json" <<JSON
{
  "run_id": "$STAMP",
  "upstream_mode": "$UPSTREAM_MODE",
  "watchdog_url": "$WATCHDOG_URL",
  "watchdog_proxy_url": "$WATCHDOG_PROXY_URL",
  "upstream_url": "$UPSTREAM_URL",
  "upstream_base_url": "$UPSTREAM_BASE_URL",
  "model": "$OPENAI_MODEL",
  "include_error_case": "$INCLUDE_ERROR_CASE",
  "kujo_bin": "$KUJO_BIN",
  "ai_sdk_path": "$AI_SDK_PATH",
  "ai_chat_bridge": "$AI_CHAT_DIR/bridge_chat.kujo",
  "watchdog_dir": "$WATCHDOG_DIR"
}
JSON

run_bridge_call "01" "Explain what Watchdog reveals when AI Chat sends a normal model request through the AI SDK." "0" "$OPENAI_MODEL"
run_bridge_call "02" "Show how Watchdog helps debug a slow latency path in an AI Chat workflow." "0" "$OPENAI_MODEL"
if [ "$INCLUDE_ERROR_CASE" = "1" ] || [ "$INCLUDE_ERROR_CASE" = "true" ]; then
	if [ "$UPSTREAM_MODE" = "fixture" ]; then
		run_bridge_call "03" "force_error: simulate a rate limit so Watchdog can capture the provider failure." "0" "$OPENAI_MODEL"
	else
		run_bridge_call "03" "Trigger a controlled provider error so Watchdog can capture failure telemetry." "0" "watchdog-demo-invalid-model"
	fi
fi

sleep 0.5

fetch_watchdog "/api/stats" "$WATCHDOG_OUT/stats.json"
fetch_watchdog "/api/requests?page_size=50" "$WATCHDOG_OUT/requests.json"
fetch_watchdog "/api/tool-calls?page_size=50" "$WATCHDOG_OUT/tool-calls.json"
fetch_watchdog "/api/agent-steps?page_size=100" "$WATCHDOG_OUT/agent-steps.json"
fetch_watchdog "/api/charts/status-breakdown" "$WATCHDOG_OUT/status-breakdown.json"
fetch_watchdog "/api/export?format=json&max_rows=200" "$WATCHDOG_OUT/export.json"

node "$ROOT/scripts/generate-report.js" "$RUN_DIR"

echo "Showcase complete:"
echo "  Summary: $RUN_DIR/summary.md"
echo "  Watchdog dashboard stayed available during run at: $WATCHDOG_URL"
