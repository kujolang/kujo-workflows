#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${1:-}"
PORT="${2:-8120}"

if [ -z "$APP_DIR" ]; then
  echo "usage: verify-app.sh <app-dir> [port]" >&2
  exit 2
fi

if [ ! -d "$APP_DIR" ]; then
  echo "App directory not found: $APP_DIR" >&2
  exit 1
fi

PUBLIC_DIR="$APP_DIR/public"
INDEX="$PUBLIC_DIR/index.php"
LOG_PREFIX="[verify-app]"
SERVER_LOG="$APP_DIR/.php-server.log"
PHP_PID=""

cleanup() {
  if [ -n "${PHP_PID:-}" ]; then
    kill "$PHP_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "$LOG_PREFIX app: $APP_DIR"
echo "$LOG_PREFIX port: $PORT"
echo "$LOG_PREFIX php: $(php -r 'echo PHP_VERSION;')"
echo

echo "$LOG_PREFIX file inventory"
find "$APP_DIR" -maxdepth 4 -type f | sort
echo

if [ ! -f "$INDEX" ]; then
  echo "$LOG_PREFIX missing public/index.php" >&2
  exit 1
fi

CSS_FILE="$(find "$PUBLIC_DIR" -path '*/assets/css/*' -type f | head -n 1 || true)"
JS_FILE="$(find "$PUBLIC_DIR" -path '*/assets/js/*' -type f | head -n 1 || true)"

if [ -z "$CSS_FILE" ]; then
  echo "$LOG_PREFIX missing CSS asset under public/assets/css" >&2
  exit 1
fi

if [ -z "$JS_FILE" ]; then
  echo "$LOG_PREFIX missing JS asset under public/assets/js" >&2
  exit 1
fi

echo "$LOG_PREFIX PHP syntax checks"
while IFS= read -r php_file; do
  echo "php -l $php_file"
  php -l "$php_file"
done < <(find "$APP_DIR" -name '*.php' -type f | sort)
echo

echo "$LOG_PREFIX content checks"
grep -qi '<!doctype html' "$INDEX"
grep -qi '<form' "$INDEX"
grep -qi 'assets/css' "$INDEX"
grep -qi 'assets/js' "$INDEX"
grep -Eq 'addEventListener|querySelector|function' "$JS_FILE"
grep -Eq '@media|grid|flex' "$CSS_FILE"
echo "index, form, CSS, and JS markers found"
echo

echo "$LOG_PREFIX selected source excerpt"
sed -n '1,80p' "$INDEX"
echo
echo "$LOG_PREFIX css excerpt"
sed -n '1,80p' "$CSS_FILE"
echo
echo "$LOG_PREFIX js excerpt"
sed -n '1,80p' "$JS_FILE"
echo

echo "$LOG_PREFIX starting PHP server"
php -S "127.0.0.1:$PORT" -t "$PUBLIC_DIR" >"$SERVER_LOG" 2>&1 &
PHP_PID="$!"

ready=0
for _ in $(seq 1 50); do
  if curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 0.1
done

if [ "$ready" -ne 1 ]; then
  echo "$LOG_PREFIX PHP server did not become ready" >&2
  cat "$SERVER_LOG" >&2 || true
  exit 1
fi

PAGE="$APP_DIR/.homepage.html"
curl -fsS "http://127.0.0.1:$PORT/" > "$PAGE"
grep -qi '</html>' "$PAGE"
grep -qi 'contact' "$PAGE"

echo "$LOG_PREFIX homepage byte count: $(wc -c < "$PAGE" | tr -d ' ')"
echo "$LOG_PREFIX homepage title:"
grep -Eio '<title>[^<]+' "$PAGE" | head -n 1 || true
echo
echo "$LOG_PREFIX verification passed"

