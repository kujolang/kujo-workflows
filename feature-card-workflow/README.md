# Feature Card Developer Workflow

This workflow is for developers who receive a task card, implement a scoped feature in an existing codebase, commit the work, and hand it to another developer or QA reviewer with proof.

It is intentionally local-first. The developer keeps all evidence in the target repo under `.kujo/feature-cards/<card-id>/`, and the reviewer starts from the handoff packet instead of reconstructing the work from chat history.

The workflow now has two modes:

- `feature-card-start` creates the run packet only.
- `feature-card-full` runs the card end to end: packet, Spec, Scout, Scent, RunLedger, Codex implementation, verification commands, Eval when present, Lens check/flow proof, PatchBrief, ChangeBucket, ShipCheck, handoff, and optional commit.

## Repo Review Summary

The sibling repos under `$KUJO_REPOS` line up as follows for this workflow:

| Stage | Repo | Role |
| --- | --- | --- |
| Card contract | `spec` | Convert the card into acceptance criteria, scope, non-goals, risks, and review expectations. |
| Codebase map | `scout` | Build a repo map with routes, dependencies, security findings, and an agent-readable summary. |
| Task context | `scent` | Package the files and git state most relevant to the card. |
| Failure/proof capture | `casefile` | Preserve failing commands, logs, and reproduction notes when work is blocked or a regression is found. |
| Browser proof | `lens` | Check the real UI, inspect selectors, execute flows, and record walkthrough evidence. |
| Deterministic checks | `eval` | Run task-specific checks with structured pass/fail reports. |
| Diff review | `patchbrief` | Summarize the implementation diff and suggest tests for reviewers. |
| Scope budget | `changebucket` | Classify the diff and catch broad or surprising changes. |
| Release gate | `shipcheck` | Run a repo readiness scan/gate before handoff. |
| Audit trail | `runledger` | Record the task lifecycle, notes, status, and final verdict. |
| Quiet runner | `muzzle` | Compress repeated noisy workflows into short summaries with logs on disk. |

`agency-runner/` is the closest existing prototype. This workflow is narrower: it assumes developers already work from cards and focuses on one feature branch from intake through reviewer handoff.

## Principles

- The card must become a verifiable contract before implementation starts.
- The developer must prove the feature against the real codebase, not only describe what changed.
- Lens proof is required for browser-visible changes and optional for backend-only work.
- Generated evidence belongs in the repo-local run folder, not in chat.
- The reviewer gets a concise packet: task, scope, diff summary, tests, Lens artifacts, known risks, and commit SHA.

## Run Folder Contract

Create one folder per task card:

```text
.kujo/feature-cards/<card-id>/
  README.md
  task/
    card.md
    assumptions.md
  spec/
    task.spec.yml
    agent-context.md
  context/
    scout/
    scent/
  implementation/
    notes.md
  eval/
    proof-plan.md
    results/
  lens/
    inspect/
    check/
    proof/
  casefile/
  briefs/
    patchbrief.md
    changebucket.md
    shipcheck.md
  ledger/
    runledger-report.md
  handoff/
    reviewer-handoff.md
    testing-request.md
  logs/
```

Keep generated `logs`, `eval/results`, and bulky recordings out of git unless the team explicitly wants proof artifacts committed. The handoff should link to the local run folder or attach selected artifacts in the card system.

## Fully Automated Run

Use this when the card should be handed to an implementation agent and then verified.

From any target repository, create a card markdown file:

```bash
cd /path/to/wordpress-plugin

cat > card.md <<'EOF'
# CARD-123 Cache jump fix

## Problem

After cached markup loads, the page jumps unexpectedly on pages using the plugin widget.

## Desired Behavior

The cached widget initializes without causing a visible page jump. Existing PHP cache behavior remains compatible.

## Acceptance Criteria

- Page position remains stable after cached markup loads.
- JavaScript initialization runs once and does not trigger duplicate layout updates.
- PHP cache keys/invalidation still work for existing plugin users.
- Existing tests pass, and browser proof is recorded with Lens.

## Verification Expectations

- Run PHP and JS checks available in the plugin.
- Use Lens against the local WordPress page that reproduces the jump.
EOF
```

Run the full workflow directly. Replace the URL and repo path for whichever project the card targets:

```bash
export KUJO_REPOS=/path/to/kujo-repos
export KUJO_WORKFLOWS="$KUJO_REPOS/kujo-workflows"
FEATURE_LENS_URL="http://127.0.0.1:8888/page-with-widget/" \
FEATURE_VERIFY_COMMANDS=$'composer validate --no-check-publish\nnpm test -- --watch=false\nnpm run build' \
"$KUJO_WORKFLOWS/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh" \
  CARD-123 \
  card.md \
  /path/to/wordpress-plugin
```

For a logged-in page, provide login details through environment variables. Use a test-only account:

```bash
export TEST_SITE_USER="test-customer@example.test"
export TEST_SITE_PASS="local-test-password"

FEATURE_LENS_URL="http://127.0.0.1:8888/my-account/" \
FEATURE_AUTH_MODE=login \
FEATURE_LOGIN_URL="http://127.0.0.1:8888/wp-login.php" \
FEATURE_LOGIN_USERNAME_ENV=TEST_SITE_USER \
FEATURE_LOGIN_PASSWORD_ENV=TEST_SITE_PASS \
FEATURE_LOGIN_SUCCESS_SELECTOR="body.logged-in" \
"$KUJO_WORKFLOWS/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh" \
  CARD-123 \
  card.md \
  /path/to/project-repo
```

Or install it into the target repo's Muzzle workflows:

```bash
mkdir -p .muzzle/workflows .muzzle/manifests
cp "$KUJO_WORKFLOWS/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh" .muzzle/workflows/
cp "$KUJO_WORKFLOWS/feature-card-workflow/muzzle-template/manifests/feature-card-full.json" .muzzle/manifests/
chmod +x .muzzle/workflows/feature-card-full.sh

FEATURE_LENS_URL="http://127.0.0.1:8888/page-with-widget/" \
muzzle run feature-card-full CARD-123 card.md /path/to/wordpress-plugin
```

The full workflow will:

1. Create `.kujo/feature-cards/CARD-123/`.
2. Add `.kujo/feature-cards/CARD-123/` to `.git/info/exclude` so proof artifacts do not pollute the implementation diff.
3. Generate and validate a Spec from the card.
4. Run Scout and Scent to build codebase/task context.
5. Start a RunLedger receipt.
6. Run a pre-fix Lens inspect/check and recorded walkthrough when `FEATURE_LENS_URL` is set.
7. Invoke Codex non-interactively to implement the card and create/update proof artifacts.
8. Run configured verification commands.
9. Run Eval if the agent creates `.kujo/feature-cards/CARD-123/eval/task.eval.json`.
10. Run post-fix Lens check and execute/record a Lens flow if one exists.
11. Generate PatchBrief, ChangeBucket, ShipCheck, RunLedger, and reviewer handoff artifacts.
12. Optionally commit code changes when `FEATURE_COMMIT=1`.

The script exits nonzero if any stage fails. It still writes the handoff and summary so reviewers can see what passed, failed, or was skipped.

Useful options:

| Variable | Purpose |
| --- | --- |
| `FEATURE_LENS_URL` | Local page URL for Lens inspect/check/proof. |
| `FEATURE_LENS_FLOW` | Existing Lens flow JSON to run before/after the fix. If omitted, a default smoke flow is generated and the agent may refine it. |
| `FEATURE_AUTH_MODE=login` | Generate an authenticated Lens flow before visiting `FEATURE_LENS_URL`. |
| `FEATURE_LOGIN_URL` | Login page URL for authenticated proof. |
| `FEATURE_LOGIN_USERNAME_ENV` / `FEATURE_LOGIN_PASSWORD_ENV` | Env var names containing test credentials. Preferred over raw values. |
| `FEATURE_LOGIN_USERNAME` / `FEATURE_LOGIN_PASSWORD` | Raw test credentials. Useful locally, but avoid shell history and never put them in card files. |
| `FEATURE_LOGIN_USER_SELECTOR` | Username input selector. Defaults cover common login forms and WordPress. |
| `FEATURE_LOGIN_PASSWORD_SELECTOR` | Password input selector. Defaults cover common login forms and WordPress. |
| `FEATURE_LOGIN_SUBMIT_SELECTOR` | Submit selector. Defaults cover common login forms and WordPress. |
| `FEATURE_LOGIN_SUCCESS_SELECTOR` / `FEATURE_LOGIN_SUCCESS_TEXT` | Optional proof that login succeeded before visiting the target URL. |
| `FEATURE_VERIFY_COMMANDS` | Newline-separated commands to run after implementation. |
| `FEATURE_SKIP_AGENT=1` | Run the workflow without letting Codex edit code. Useful for dry runs. |
| `FEATURE_IMPLEMENT_COMMAND` | Use a custom implementation command instead of Codex. |
| `FEATURE_BRANCH` | Branch to create or switch to. Default: `feature/<card-id>`. |
| `FEATURE_COMMIT=1` | Commit code changes at the end. Generated `.kujo/feature-cards/<id>/` artifacts stay uncommitted by default. |
| `FEATURE_CODEX_MODEL` | Optional Codex model override. |
| `FEATURE_MAX_FILES` / `FEATURE_MAX_CHURN` | ChangeBucket budget thresholds. |

Authentication note: the generated Lens flow must contain the runtime password value so Lens can type it. The password step is marked `"secret": true`, Lens redacts it in artifacts, and `.kujo/feature-cards/<card-id>/` is added to `.git/info/exclude`. Still use test-only credentials and review artifacts before sharing.

Review results here:

```text
.kujo/feature-cards/CARD-123/summary.md
.kujo/feature-cards/CARD-123/status.tsv
.kujo/feature-cards/CARD-123/handoff/reviewer-handoff.md
.kujo/feature-cards/CARD-123/handoff/testing-request.md
.kujo/feature-cards/CARD-123/lens/pre-fix/flow/walkthrough.html
.kujo/feature-cards/CARD-123/lens/proof/walkthrough.html
.kujo/feature-cards/CARD-123/briefs/patchbrief.md
.kujo/feature-cards/CARD-123/briefs/changebucket.md
.kujo/feature-cards/CARD-123/briefs/shipcheck.md
.kujo/feature-cards/CARD-123/ledger/runledger-report.md
```

## Manual / Composable Workflow

### 1. Intake The Card

Start from the task card, not from a vague branch name.

Required card fields:

- Card ID and title
- Problem statement
- User-visible behavior
- Acceptance criteria
- In-scope files, routes, screens, or services if known
- Explicit non-goals
- Test expectations
- Reviewer or QA owner

Use `templates/task-card.md` when the card system does not already enforce these fields.

### 2. Create The Local Run Packet

Use the Muzzle template in this folder, or create the run folder manually.

```bash
mkdir -p .kujo/feature-cards/CARD-123/{task,spec,context/scout,context/scent,implementation,eval/results,lens/inspect,lens/check,lens/proof,casefile,briefs,ledger,handoff,logs}
cp task.md .kujo/feature-cards/CARD-123/task/card.md
```

If Muzzle is available, copy the template into the target repo once:

```bash
mkdir -p .muzzle/workflows .muzzle/manifests
cp "$KUJO_WORKFLOWS/feature-card-workflow/muzzle-template/workflows/feature-card-start.sh" .muzzle/workflows/
cp "$KUJO_WORKFLOWS/feature-card-workflow/muzzle-template/manifests/feature-card-start.json" .muzzle/manifests/
chmod +x .muzzle/workflows/feature-card-start.sh
muzzle run feature-card-start CARD-123 task.md
```

Start a RunLedger entry if the team wants an audit receipt for the card:

```bash
export KUJO_REPOS=/path/to/kujo-repos
export KUJO="$KUJO_REPOS/kujo/target/release/kujo"
export PATH="$KUJO_REPOS/runledger/bin:$PATH"

runledger start \
  --provider human \
  --model developer \
  --task "CARD-123 short feature name" \
  --prompt .kujo/feature-cards/CARD-123/task/card.md \
  --repo .
```

### 3. Turn The Card Into A Spec

Write `.kujo/feature-cards/<card-id>/spec/task.spec.yml` from the card. It should contain goal, scope, non-goals, acceptance criteria, eval requirements, risks, dependencies, and review expectations.

```bash
export KUJO_REPOS=/path/to/kujo-repos
export PATH="$KUJO_REPOS/spec/scripts:$PATH"
export KUJO_BIN="$KUJO_REPOS/kujo/target/release/kujo"
export KUJO="$KUJO_BIN"

spec validate .kujo/feature-cards/CARD-123/spec/task.spec.yml
spec render .kujo/feature-cards/CARD-123/spec/task.spec.yml \
  --output .kujo/feature-cards/CARD-123/spec/task.spec.md
spec export-agent-context .kujo/feature-cards/CARD-123/spec/task.spec.yml \
  --output .kujo/feature-cards/CARD-123/spec/agent-context.md
```

If acceptance criteria cannot be checked, stop and clarify the card before editing code.

### 4. Build Context Before Editing

Run Scout once to map the repo and Scent once to create task-specific context.

```bash
"$KUJO_BIN" run "$KUJO_REPOS/scout/scout.kujo" -- . \
  --quick \
  -o .kujo/feature-cards/CARD-123/context/scout

"$KUJO_BIN" run "$KUJO_REPOS/scent/scent.kujo" pack \
  --task "$(sed -n '1,40p' .kujo/feature-cards/CARD-123/task/card.md)" \
  --out .kujo/feature-cards/CARD-123/context/scent \
  --format both
```

For UI work, run Lens inspect before writing flow assertions:

```bash
"$KUJO_REPOS/lens/lens" inspect http://127.0.0.1:3000/path \
  --json \
  --out .kujo/feature-cards/CARD-123/lens/inspect
```

### 5. Implement On A Feature Branch

Branch from the current integration branch:

```bash
git switch -c feature/CARD-123-short-name
```

Work in small commits or a clean working set. Record meaningful notes in:

```text
.kujo/feature-cards/CARD-123/implementation/notes.md
```

If a command failure is important for review or diagnosis, capture it:

```bash
"$KUJO_BIN" run --interpreter "$KUJO_REPOS/casefile/casefile.kujo" -- capture \
  --name card-123-failing-test \
  --output-dir .kujo/feature-cards/CARD-123/casefile \
  -- npm test -- --runInBand
```

### 6. Prove The Work

Use `templates/proof-plan.md` to decide the exact checks before calling the work done.

Minimum proof by change type:

| Change type | Required proof |
| --- | --- |
| Browser UI | Unit/integration checks, Lens `check`, Lens `flow --execute --record --walkthrough`. |
| API/backend | Unit/integration checks, HTTP or contract checks through Eval. |
| Data/model | Migration or fixture checks, rollback notes, data validation. |
| AI/agent behavior | Deterministic fixture calls, Watchdog telemetry when useful, Eval output checks. |
| Docs/config only | Link/render/config validation and PatchBrief summary. |

Example Lens proof:

```bash
"$KUJO_REPOS/lens/lens" check http://127.0.0.1:3000/path \
  --viewport mobile \
  --viewport desktop \
  --accessibility \
  --html \
  --out .kujo/feature-cards/CARD-123/lens/check

"$KUJO_REPOS/lens/lens" flow .kujo/feature-cards/CARD-123/lens/feature.flow.json \
  --execute \
  --record \
  --walkthrough \
  --out .kujo/feature-cards/CARD-123/lens/proof
```

Example Eval run:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/eval/main.kujo" run .kujo/feature-cards/CARD-123/eval/task.eval.json \
  --out .kujo/feature-cards/CARD-123/eval/results
```

### 7. Package The Review

Generate reviewer-facing summaries from the final diff:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/patchbrief/patchbrief.kujo" -- summarize \
  > .kujo/feature-cards/CARD-123/briefs/patchbrief.md

"$KUJO_BIN" run "$KUJO_REPOS/patchbrief/patchbrief.kujo" -- suggest-tests \
  > .kujo/feature-cards/CARD-123/briefs/test-suggestions.md

KUJO="$KUJO_BIN" "$KUJO_REPOS/changebucket/bin/changebucket" --markdown \
  > .kujo/feature-cards/CARD-123/briefs/changebucket.md

"$KUJO_BIN" run "$KUJO_REPOS/shipcheck/shipcheck.kujo" scan --dir . \
  > .kujo/feature-cards/CARD-123/briefs/shipcheck.md
```

If the team wants a blocking pre-review gate:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/shipcheck/shipcheck.kujo" gate --dir . --format json \
  > .kujo/feature-cards/CARD-123/briefs/shipcheck-gate.json
```

### 8. Commit And Handoff

Commit only the intended code, tests, and durable docs. Do not accidentally commit local proof folders unless your team policy says to.

```bash
git status --short
git diff --stat
git add <intended files>
git commit -m "CARD-123: implement short feature name"
```

Finish the RunLedger record if one was started:

```bash
runledger note <run-id> "Verification completed; see .kujo/feature-cards/CARD-123."
runledger finish <run-id> \
  --status pass \
  --verdict "CARD-123 implemented and ready for developer testing." \
  --repo .
runledger report \
  --task "CARD-123 short feature name" \
  --output .kujo/feature-cards/CARD-123/ledger/runledger-report.md
```

Create `handoff/reviewer-handoff.md` from the template. It must include:

- Card ID and branch
- Commit SHA
- Scope summary
- Files changed
- Test commands and results
- Lens report/walkthrough paths when applicable
- Known risks and follow-ups
- Reviewer focus areas

Then move the card to testing and attach the handoff or paste its concise summary.

## Done Definition

A feature card is ready for developer testing when all of these are true:

- Spec acceptance criteria are explicit and matched by proof.
- The working tree contains only intended changes.
- Required automated tests pass or documented failures are captured in CaseFile.
- Lens proof exists for user-visible browser behavior.
- PatchBrief and test suggestions are generated.
- ShipCheck has no unresolved error-level blockers, or blockers are explicitly accepted.
- The reviewer handoff names what changed, how it was verified, and what still needs attention.

## Where This Fits

This workflow can become a future `agency-runner` mode:

```text
card intake -> spec -> context -> implement -> proof -> review packet -> commit -> testing
```

For now, it is deliberately copyable: one team can adopt the folder contract and templates without waiting for a new core command.
