#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PREFIX=""
SOURCE_REPOS="$(cd "$ROOT/.." && pwd)"
KUJO_SOURCE="${KUJO_BIN:-$SOURCE_REPOS/kujo/target/release/kujo}"
RUN_DEMO=0

usage() {
  echo "usage: $0 --prefix ABSOLUTE_PATH [--source-repos PATH] [--kujo-bin PATH] [--demo]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix) PREFIX="${2:-}"; shift 2 ;;
    --source-repos) SOURCE_REPOS="${2:-}"; shift 2 ;;
    --kujo-bin) KUJO_SOURCE="${2:-}"; shift 2 ;;
    --demo) RUN_DEMO=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

if [[ -z "$PREFIX" || "$PREFIX" != /* || "$PREFIX" == "/" ]]; then
  echo "--prefix must be a non-root absolute path" >&2
  exit 2
fi
if [[ -e "$PREFIX" ]]; then
  echo "installation target already exists: $PREFIX" >&2
  exit 2
fi
if [[ ! -x "$KUJO_SOURCE" ]]; then
  echo "Kujo binary is not executable: $KUJO_SOURCE" >&2
  exit 2
fi

PARENT="$(dirname "$PREFIX")"
mkdir -p "$PARENT"
STAGE="$(mktemp -d "$PARENT/.publishing-house-install.XXXXXX")"
trap 'rm -rf -- "$STAGE"' EXIT
mkdir -p "$STAGE/kujo-workflows" "$STAGE/repos" "$STAGE/bin"

if [[ -d "$ROOT/.git" ]]; then
  git -C "$ROOT" archive --format=tar HEAD | tar -xf - -C "$STAGE/kujo-workflows"
else
  echo "installer must run from a Git checkout so only tracked files are installed" >&2
  exit 2
fi

while IFS=$'\t' read -r name commit url; do
  if [[ -d "$SOURCE_REPOS/$name/.git" ]]; then
    git clone --quiet --no-checkout --local --no-hardlinks "$SOURCE_REPOS/$name" "$STAGE/repos/$name"
  else
    git clone --quiet --no-checkout "$url" "$STAGE/repos/$name"
  fi
  git -C "$STAGE/repos/$name" checkout --quiet --detach "$commit"
done < <("$KUJO_SOURCE" run "$ROOT/scripts/publishing_house_doctor.kujo" -- --install-lines)

cp "$KUJO_SOURCE" "$STAGE/bin/kujo"
chmod 0755 "$STAGE/bin/kujo"

cat >"$STAGE/bin/publishing-house-doctor" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
INSTALL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export KUJO_REPOS="$INSTALL_ROOT/repos"
export KUJO_BIN="$INSTALL_ROOT/bin/kujo"
exec "$INSTALL_ROOT/kujo-workflows/scripts/publishing-house-doctor" "$@"
EOF
cat >"$STAGE/bin/publishing-house-demo" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
INSTALL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export KUJO_REPOS="$INSTALL_ROOT/repos"
export KUJO_BIN="$INSTALL_ROOT/bin/kujo"
exec "$INSTALL_ROOT/kujo-workflows/scripts/run-publishing-house-fixture.sh" "$@"
EOF
chmod 0755 "$STAGE/bin/publishing-house-doctor" "$STAGE/bin/publishing-house-demo"

KUJO_REPOS="$STAGE/repos" KUJO_BIN="$STAGE/bin/kujo" "$STAGE/kujo-workflows/scripts/publishing-house-doctor" >/dev/null
mv "$STAGE" "$PREFIX"
trap - EXIT
if [[ "$RUN_DEMO" -eq 1 ]]; then
  "$PREFIX/bin/publishing-house-demo" --out "$PREFIX/first-run" >/dev/null
fi
echo "Publishing House installed at $PREFIX"
echo "Doctor: $PREFIX/bin/publishing-house-doctor"
echo "Fixture: $PREFIX/bin/publishing-house-demo --out $PREFIX/runs/first-run"
