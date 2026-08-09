# CaseFile Incident Evidence Packet HOWTO

## 1. Run The Demo

```bash
cd casefile-incident-evidence-packet
bash scripts/run-workflow.sh
```

## 2. Review The Case

Open:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/logs/capture.log
.runs/<timestamp>/logs/show-latest.md
.runs/<timestamp>/logs/show-latest.json
```

Then inspect the case bundle:

```text
.runs/<timestamp>/fixture/.casefile/<case-id>/case.md
.runs/<timestamp>/fixture/.casefile/<case-id>/case.json
.runs/<timestamp>/fixture/.casefile/<case-id>/combined.log
.runs/<timestamp>/fixture/.casefile/<case-id>/reproduction.md
.runs/<timestamp>/fixture/.casefile/<case-id>/handoff.md
```

## 3. Capture A Real Failure

From a target repo:

```bash
export KUJO_REPOS=/path/to/kujo-repos
export KUJO_BIN="$KUJO_REPOS/kujo/target/release/kujo"
"$KUJO_BIN" run --interpreter "$KUJO_REPOS/casefile/casefile.kujo" -- init
"$KUJO_BIN" run --interpreter "$KUJO_REPOS/casefile/casefile.kujo" -- capture --name failing-tests -- npm test
```

Use `--mirror-exit-code` in CI when the capture should preserve the command's failure status.

## 4. Content Notes

The clearest demo is a side-by-side of a raw failing command and the generated `handoff.md`. CaseFile turns failure into something another developer or agent can act on.

## 5. Troubleshooting

CaseFile writes `.casefile/` under the current repo. This workflow runs inside an isolated fixture repo under `.runs/<timestamp>/fixture/`.
