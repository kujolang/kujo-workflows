#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 8 ]; then
  echo "usage: ai-request.sh <provider> <model> <prompt-file> <result-file> <ai-sdk-dir> <kujo-bin> <max-tokens> <request-script>" >&2
  exit 2
fi

PROVIDER="$1"
MODEL="$2"
PROMPT_FILE="$3"
RESULT_FILE="$4"
AI_SDK_DIR="$5"
KUJO_BIN="$6"
MAX_TOKENS="$7"
REQUEST_SCRIPT="$8"

TEMPERATURE="${TEMPERATURE:-0.2}"

if [ ! -x "$KUJO_BIN" ]; then
  echo "Kujo runtime not executable: $KUJO_BIN" >&2
  exit 1
fi

if [ ! -d "$AI_SDK_DIR" ]; then
  echo "AI SDK directory not found: $AI_SDK_DIR" >&2
  exit 1
fi

if [ ! -f "$REQUEST_SCRIPT" ]; then
  echo "AI SDK request script not found: $REQUEST_SCRIPT" >&2
  exit 1
fi

mkdir -p "$(dirname "$RESULT_FILE")"

echo "AI SDK request"
echo "Provider: $PROVIDER"
echo "Model: ${MODEL:-provider-default}"
echo "Prompt: $PROMPT_FILE"
echo "Result: $RESULT_FILE"
echo "Max tokens: $MAX_TOKENS"
echo

(
  cd "$AI_SDK_DIR"
  BENCH_PROVIDER="$PROVIDER" \
    BENCH_MODEL="$MODEL" \
    BENCH_PROMPT_FILE="$PROMPT_FILE" \
    BENCH_RESULT_FILE="$RESULT_FILE" \
    BENCH_MAX_TOKENS="$MAX_TOKENS" \
    BENCH_TEMPERATURE="$TEMPERATURE" \
    "$KUJO_BIN" run "$REQUEST_SCRIPT"
)

