# Agency Verified Fix Loop HOWTO

This tutorial shows how the Kujo tool ecosystem can turn a normal agency bug-fix request into a scoped, tracked, tested, browser-verified, client-ready delivery packet.

The example is fictional, but the workflow is intentionally practical: a developer receives a vague client task for a PHP/JavaScript/CSS storefront, converts it into a structured implementation contract, runs the work with evidence capture, verifies the result with deterministic tests and Lens browser proof, then hands the client a concise proof bundle.

## Runnable Demo Kit

A runnable automation kit for this tutorial lives beside this HOWTO:

```text
agency-verified-fix-loop/
```

From that folder, run:

```bash
STRICT=1 bash scripts/run-loop.sh
```

The kit creates a temporary buggy PHP/JS/CSS storefront, proves the Lens flow fails before the fix, applies a deterministic JS/CSS fix, runs Spec, Scout, Scent, Eval, Lens, PatchBrief, ChangeBucket, ShipCheck, and RunLedger, then writes a client handoff packet under `.runs/<timestamp>/client/`.

## What This Workflow Proves

The Agency Verified Fix Loop is designed to answer the questions clients, PMs, reviewers, and cautious developers always ask after AI-assisted work:

- What exactly was the task?
- What was in scope and out of scope?
- What context did the agent use?
- What changed?
- How large or risky was the change?
- Which checks passed?
- Can we replay the user-facing fix?
- Where is the audit trail?
- What should a human review next?

The workflow is not just "AI wrote some code." It is a chain of reviewable artifacts.

```text
Client task
  -> Spec task contract
  -> Scout repo map
  -> Scent task context pack
  -> PackWrite agent execution pack
  -> RunLedger run record
  -> Implementation work
  -> Eval deterministic checks
  -> Lens browser proof + walkthrough
  -> PatchBrief diff explanation
  -> ChangeBucket blast-radius report
  -> ShipCheck release gate
  -> Final client handoff
```

## Fictional Client Request

Imagine the agency maintains a small PHP storefront for a client called **Northstar Outfitters**.

The stack is deliberately ordinary:

- PHP templates and controllers
- vanilla JavaScript
- plain CSS
- no full SPA framework
- a local dev server at `http://127.0.0.1:8080`

The client sends this task:

> On mobile, the cart promo-code drawer is broken. When customers tap "Have a promo code?", the drawer opens but the input is hidden behind the sticky checkout bar. Some users also report that tapping Apply does nothing the first time. Please fix it without redesigning the cart page. We need proof that the promo drawer works on mobile before pushing to production.

The target repository is fictional:

```text
northstar-storefront/
  public/
    cart.php
    checkout.php
  src/
    CartController.php
    PromoCodeService.php
  assets/
    js/cart.js
    css/cart.css
  tests/
    promo_code_test.php
  package.json
  composer.json
```

The suspected bug is in:

- `public/cart.php`
- `assets/js/cart.js`
- `assets/css/cart.css`

But we do not assume that yet. The loop forces us to discover, scope, verify, and prove.

## Tools Used

| Tool | Role In The Loop |
|---|---|
| Spec | Converts the client request into a structured task contract |
| Scout | Maps the repo: files, languages, routes, dependencies, risk signals |
| Scent | Builds a bounded, task-specific context pack |
| PackWrite | Produces an implementation-agent pack from the task/context |
| RunLedger | Records the run, model/provider, git state, notes, usage, verdict |
| Dispatch | Optional orchestration layer for multi-step/policy-gated execution |
| Eval | Runs deterministic checks against commands/files/HTTP/JSON outputs |
| Lens | Opens the app, executes the mobile flow, records proof, writes walkthrough |
| PatchBrief | Summarizes the final git diff for reviewers |
| ChangeBucket | Measures blast radius and ChangeBucket scope compliance |
| Fence | Optional architecture-boundary check |
| CaseFile | Captures failures as reproducible case bundles when a command fails |
| ShipCheck | Runs release-readiness checks before handoff |

This HOWTO shows the manual choreography. A future wrapper could make this one command, but the underlying artifacts should remain visible.

## Prerequisites

Set these paths for your local Kujo ecosystem checkout:

```bash
export KUJO_REPOS="/Users/robertdevore/2026/Kujolang/kujo-repos"
export KUJO_BIN="$KUJO_REPOS/kujo/target/release/kujo"

export PATH="$KUJO_REPOS/spec/scripts:$PATH"
export PATH="$KUJO_REPOS/lens:$PATH"
export PATH="$KUJO_REPOS/runledger/bin:$PATH"
export PATH="$KUJO_REPOS/changebucket/bin:$PATH"
export PATH="$KUJO_REPOS/packwrite/bin:$PATH"
```

For the fictional project:

```bash
cd /path/to/northstar-storefront
git status --short
```

Start from a clean branch when possible:

```bash
git checkout -b fix/mobile-promo-drawer
```

Create a workspace for workflow artifacts:

```bash
mkdir -p .kujo-agency-loop/{spec,scout,scent,pack,eval,lens,briefs,client}
```

## Step 1: Capture The Client Task As A Spec

Create a spec file from the raw client task:

```bash
spec init \
  --name "Fix mobile promo-code drawer on cart page" \
  --output .kujo-agency-loop/spec/mobile-promo-drawer.spec.yml
```

Then edit the spec so it is concrete and testable:

```yaml
name: "Fix mobile promo-code drawer on cart page"
goal: "Fix the mobile cart promo-code drawer so customers can reveal the input, enter a promo code, apply it on the first tap, and continue checkout without the sticky checkout bar covering the form."
version: "0.1.0"
priority: "high"
tags:
  - agency
  - storefront
  - mobile
  - cart
  - bugfix

background: >
  Client reports that mobile customers can open the promo-code drawer, but the
  input is hidden behind the sticky checkout bar. Some users also report that
  the Apply button does nothing on the first tap.

scope: >
  Investigate and fix the promo-code drawer behavior on the cart page for mobile
  viewport sizes. Preserve the existing cart layout and visual style.

non_goals:
  - "Redesigning the cart page"
  - "Changing checkout payment behavior"
  - "Changing promo-code validation rules"
  - "Adding a JavaScript framework"

relevant_systems:
  - "public/cart.php"
  - "assets/js/cart.js"
  - "assets/css/cart.css"
  - "src/PromoCodeService.php"
  - "tests/promo_code_test.php"

likely_files:
  - "public/cart.php"
  - "assets/js/cart.js"
  - "assets/css/cart.css"
  - "tests/promo_code_test.php"

acceptance_criteria:
  - "At mobile width, tapping 'Have a promo code?' reveals the promo-code drawer."
  - "The promo-code input is visible and not covered by the sticky checkout bar."
  - "Entering SAVE10 and tapping Apply applies the code on the first tap."
  - "A success message is visible after applying a valid promo code."
  - "Existing desktop cart layout remains unchanged."
  - "No console errors occur during the promo-code flow."
  - "No PHP promo-code tests regress."

eval_requirements:
  - description: "PHP promo-code tests pass"
    check_type: "command_succeeds"
    params:
      command: "composer test -- tests/promo_code_test.php"
  - description: "Cart JavaScript lint passes"
    check_type: "command_succeeds"
    params:
      command: "npm run lint -- assets/js/cart.js"
  - description: "Cart page responds locally"
    check_type: "http_status"
    params:
      url: "http://127.0.0.1:8080/cart.php"
      expected_status: 200

risks:
  - risk: "Changing sticky checkout CSS could affect checkout conversion layout."
    severity: "medium"
    mitigation: "Limit CSS changes to cart promo drawer/mobile breakpoint and verify desktop with Lens."
  - risk: "JavaScript event binding fix could duplicate promo submission."
    severity: "medium"
    mitigation: "Use deterministic event delegation and verify one first-tap apply path."

review_expectations:
  - "Reviewer should inspect mobile CSS changes."
  - "Reviewer should confirm no promo validation logic was changed unnecessarily."
  - "Reviewer should review Lens walkthrough proof."

human_approval_points:
  - "Before production deploy"
```

Validate and render it:

```bash
spec validate .kujo-agency-loop/spec/mobile-promo-drawer.spec.yml --strict
spec render .kujo-agency-loop/spec/mobile-promo-drawer.spec.yml \
  --output .kujo-agency-loop/spec/mobile-promo-drawer.md
```

Export the agent context and Eval suite:

```bash
spec export-agent-context .kujo-agency-loop/spec/mobile-promo-drawer.spec.yml \
  --output .kujo-agency-loop/spec/agent-context.md

spec export-eval .kujo-agency-loop/spec/mobile-promo-drawer.spec.yml \
  --output .kujo-agency-loop/eval/mobile-promo-drawer.eval.json
```

Expected artifacts:

```text
.kujo-agency-loop/spec/
  mobile-promo-drawer.spec.yml
  mobile-promo-drawer.md
  agent-context.md

.kujo-agency-loop/eval/
  mobile-promo-drawer.eval.json
```

The agency value: the vague client request is now a contract with explicit acceptance criteria, non-goals, risks, and checks.

## Step 2: Map The Repository With Scout

Run Scout to create a repo intelligence pack:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/scout/scout.kujo" -- . \
  --output .kujo-agency-loop/scout \
  --max-depth 5 \
  --security-export sarif
```

Scout produces an agent-readable map:

```text
.kujo-agency-loop/scout/<project-run>/
  README.md
  FILE_TREE.md
  AGENTS.md
  CHECKLIST.md
  llms.txt
  intelligence.json
  scan_manifest.json
  security.sarif
```

Use this to avoid the classic agent failure mode: editing files before understanding the project.

In the fictional project, Scout might identify:

- PHP files under `public/` and `src/`
- route-like pages such as `public/cart.php`
- JavaScript behavior under `assets/js/cart.js`
- CSS under `assets/css/cart.css`
- dependency manifests `composer.json` and `package.json`
- security findings, if any, unrelated to the promo drawer

The agency value: the agent and developer share the same repo map before implementation starts.

## Step 3: Build A Task-Specific Context Pack With Scent

Scout maps the whole repo. Scent narrows context to this task.

```bash
"$KUJO_BIN" run "$KUJO_REPOS/scent/scent.kujo" pack \
  --task "Fix the mobile cart promo-code drawer so the input is visible and Apply works on first tap." \
  --out .kujo-agency-loop/scent \
  --target codex \
  --include public/cart.php \
  --include assets/js/cart.js \
  --include assets/css/cart.css \
  --include src/PromoCodeService.php \
  --include tests/promo_code_test.php \
  --max-files 20 \
  --max-file-bytes 60000 \
  --format both
```

Expected artifacts:

```text
.kujo-agency-loop/scent/
  context.md
  context.json
  files.json
  manifest.json
  metadata.json
  redactions.json
```

Review `redactions.json` before sending context to any model-backed step.

The agency value: context is bounded, reviewable, redacted, and task-specific.

## Step 4: Generate The Agent Execution Pack With PackWrite

Create a task brief for PackWrite. This can combine the original client task, Spec summary, Scout summary, and Scent context summary.

```bash
cat > .kujo-agency-loop/pack/MEGA_PROMPT.md <<'PROMPT'
# Client Task

On mobile, the cart promo-code drawer is broken. When customers tap "Have a promo code?", the drawer opens but the input is hidden behind the sticky checkout bar. Some users also report that tapping Apply does nothing the first time.

# Goal

Fix the mobile promo-code drawer without redesigning the cart page.

# Acceptance Criteria

- At mobile width, tapping "Have a promo code?" reveals the promo-code drawer.
- The promo-code input is visible and not covered by the sticky checkout bar.
- Entering SAVE10 and tapping Apply applies the code on the first tap.
- A success message is visible after applying a valid promo code.
- Existing desktop cart layout remains unchanged.
- No console errors occur during the promo-code flow.
- Existing PHP promo-code tests pass.

# Relevant Files

- public/cart.php
- assets/js/cart.js
- assets/css/cart.css
- src/PromoCodeService.php
- tests/promo_code_test.php

# Guardrails

- Do not redesign the cart page.
- Do not change promo-code business rules unless a test proves they are wrong.
- Prefer the smallest fix that satisfies the acceptance criteria.
- Add or update tests only where they directly prove the fix.
- Produce notes suitable for client handoff.
PROMPT
```

Set the provider key through the environment, then run PackWrite in dry-run mode first:

```bash
export PACKWRITE_API_KEY="replace-with-provider-key"
```

```bash
packwrite init .kujo-agency-loop/pack/MEGA_PROMPT.md \
  --provider openai \
  --model gpt-4.1-mini \
  --output .kujo-agency-loop/pack/agent \
  --dry-run
```

Then generate the pack:

```bash
packwrite init .kujo-agency-loop/pack/MEGA_PROMPT.md \
  --provider openai \
  --model gpt-4.1-mini \
  --output .kujo-agency-loop/pack/agent
```

Validate it:

```bash
packwrite validate --output .kujo-agency-loop/pack/agent
```

Expected pack:

```text
.kujo-agency-loop/pack/agent/
  MASTER.md
  TODO.md
  HANDOFF.md
  DECISIONS.md
  REVIEW_CHECKLIST.md
  DEEPSEEK_START.md
  CODEX_REVIEW_PROMPT.md
  phases/
    00-project-brief.md
    01-investigate-mobile-drawer.md
    02-fix-event-binding.md
    03-fix-mobile-layout.md
    04-add-regression-checks.md
    05-run-proof-and-handoff.md
```

The agency value: the agent gets a phase-by-phase operating manual instead of one giant fuzzy prompt.

## Step 5: Start The RunLedger Record

Start a run before implementation begins:

```bash
runledger start \
  --provider openai \
  --model gpt-4.1-mini \
  --task "Northstar mobile promo drawer fix" \
  --prompt .kujo-agency-loop/spec/agent-context.md \
  --repo .
```

The command prints a line like:

```text
Started run: 2026-06-11-gpt-4-1-mini-northstar-mobile-promo-drawer-fix-001
```

Copy that value into `RUN_ID` for the remaining commands:

```bash
export RUN_ID="2026-06-11-gpt-4-1-mini-northstar-mobile-promo-drawer-fix-001"
```

Add the initial note:

```bash
runledger note "$RUN_ID" "Started from client request. Spec, Scout, Scent, and PackWrite artifacts created under .kujo-agency-loop/."
```

The agency value: before any code changes, the run has a timestamp, model/provider, prompt artifact, start commit, and dirty-state baseline.

## Step 6: Optional Dispatch Orchestration

For a first demo, you can do the work directly from the PackWrite agent pack.

For a more controlled multi-step story, Dispatch can orchestrate a policy-gated workflow and produce run state, trace, report, and handoff artifacts.

Current Dispatch is template-driven, so today this step is best used as a wrapper-friendly orchestration demonstration rather than direct Spec ingestion:

```bash
"$KUJO_BIN" run --interpreter "$KUJO_REPOS/dispatch/dispatch.kujo" demo \
  "Northstar mobile promo drawer fix" \
  --workflow crud-reliability \
  --yes \
  --output-root .kujo-agency-loop/dispatch \
  --tags agency,northstar,mobile-cart
```

Expected artifacts:

```text
.kujo-agency-loop/dispatch/<run-id>/
  state.json
  trace.json
  trace.md
  report.md
  report.json
```

Future ideal wrapper:

```bash
kujo agency-loop run .kujo-agency-loop/spec/mobile-promo-drawer.spec.yml
```

The agency value: orchestration produces a replayable state machine and trace instead of an invisible chat transcript.

## Step 7: Implement The Fix

The implementation agent reads:

- `.kujo-agency-loop/pack/agent/MASTER.md`
- `.kujo-agency-loop/pack/agent/TODO.md`
- `.kujo-agency-loop/pack/agent/phases/*.md`
- `.kujo-agency-loop/scent/context.md`
- `.kujo-agency-loop/spec/mobile-promo-drawer.md`

The actual code changes are not prescribed by this HOWTO, but the fictional fix might be:

- In `assets/js/cart.js`, bind the Apply handler through stable event delegation on the cart form instead of binding before the drawer exists.
- In `assets/js/cart.js`, remove a duplicate one-time click guard that caused the first tap to only initialize the handler.
- In `assets/css/cart.css`, add mobile bottom padding to the promo drawer equal to the sticky checkout bar height.
- In `assets/css/cart.css`, ensure the promo drawer scrolls into view when opened.
- In `public/cart.php`, add or confirm stable selectors such as `data-testid="promo-toggle"`, `data-testid="promo-input"`, and `data-testid="promo-apply"` for browser proof.
- In `tests/promo_code_test.php`, add a regression assertion that a valid promo code still applies exactly once.

After each meaningful phase, update the ledger:

```bash
runledger note "$RUN_ID" "Investigated cart promo drawer. Suspected first-tap failure is JS event binding; visibility issue is mobile sticky checkout overlap."
runledger note "$RUN_ID" "Implemented scoped JS/CSS fix. No promo-code service rules changed."
```

The agency value: implementation is not a black box. It is phase-based and narrated.

## Step 8: Capture Failures With CaseFile When Needed

If a validation command fails, capture it instead of pasting raw logs into chat:

```bash
"$KUJO_BIN" run --interpreter "$KUJO_REPOS/casefile/casefile.kujo" -- capture \
  --name promo-code-php-test-failure \
  --output-dir .kujo-agency-loop/casefile \
  -- composer test -- tests/promo_code_test.php
```

Expected case bundle:

```text
.kujo-agency-loop/casefile/<timestamp-promo-code-php-test-failure>/
  case.md
  case.json
  command.txt
  stdout.log
  stderr.log
  combined.log
  git-status.txt
  git-diff-stat.txt
  environment.json
  reproduction.md
  handoff.md
```

Add it to the ledger:

```bash
runledger note "$RUN_ID" "Captured failing PHP promo-code test in CaseFile and used reproduction notes to fix regression."
```

The agency value: failures become structured evidence, not lost terminal noise.

## Step 9: Run Deterministic Eval Checks

Run the Eval suite exported from the Spec:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/eval/main.kujo" run \
  .kujo-agency-loop/eval/mobile-promo-drawer.eval.json \
  --output-dir .kujo-agency-loop/eval/results \
  --artifact-checksums \
  --json
```

Verify the artifact manifest:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/eval/main.kujo" verify-manifest \
  --output-dir .kujo-agency-loop/eval/results \
  --json
```

Expected artifacts:

```text
.kujo-agency-loop/eval/results/
  summary.json
  artifact-manifest.json
  cli-summary.json
  last_run.json
  eval-report.md
```

Add the result:

```bash
runledger note "$RUN_ID" "Eval checks passed: PHP promo-code tests, JS lint, local cart HTTP status."
```

The agency value: acceptance checks are deterministic and artifact-backed.

## Step 10: Use Lens To Inspect The UI

Start the local storefront:

```bash
php -S 127.0.0.1:8080 -t public
```

Run a read-only Lens check first:

```bash
lens check http://127.0.0.1:8080/cart.php \
  --viewport mobile \
  --viewport desktop \
  --accessibility \
  --html \
  --out .kujo-agency-loop/lens/check
```

Then inspect the cart page for real selectors:

```bash
lens inspect http://127.0.0.1:8080/cart.php \
  --json \
  --out .kujo-agency-loop/lens/inspect
```

Expected inspect output should include selectors like:

```text
[button] "Have a promo code?" -> [data-testid=promo-toggle]
[input:text] "Promo code" -> [data-testid=promo-input]
[button] "Apply" -> [data-testid=promo-apply]
```

The agency value: the browser flow is based on real DOM evidence, not guessed selectors.

## Step 11: Author The Lens Proof Flow

Create a Lens flow file:

```json
{
  "name": "Mobile promo-code drawer applies code",
  "url": "http://127.0.0.1:8080/cart.php",
  "viewports": ["mobile"],
  "timeout_seconds": 20,
  "allow_external": false,
  "allow_destructive": false,
  "steps": [
    {
      "visit": "http://127.0.0.1:8080/cart.php"
    },
    {
      "assert_text": "Have a promo code?"
    },
    {
      "click": {
        "selector": "[data-testid=promo-toggle]",
        "safe": true
      }
    },
    {
      "wait_for_selector": "[data-testid=promo-input]"
    },
    {
      "screenshot": {
        "name": "promo-drawer-open"
      }
    },
    {
      "type": {
        "selector": "[data-testid=promo-input]",
        "value": "SAVE10"
      }
    },
    {
      "click": {
        "selector": "[data-testid=promo-apply]",
        "safe": true
      }
    },
    {
      "wait_for_text": "Promo code applied"
    },
    {
      "assert_text": "Promo code applied"
    },
    {
      "assert_no_console_errors": true
    },
    {
      "assert_no_failed_requests": true
    },
    {
      "screenshot": {
        "name": "promo-applied"
      }
    }
  ]
}
```

Save it as:

```text
.kujo-agency-loop/lens/mobile-promo-drawer.flow.json
```

Validate the flow without executing it:

```bash
lens flow .kujo-agency-loop/lens/mobile-promo-drawer.flow.json \
  --validate \
  --json
```

The agency value: the proof flow has a safety gate before it clicks anything.

## Step 12: Execute The Lens Flow And Record Proof

Run the flow:

```bash
lens flow .kujo-agency-loop/lens/mobile-promo-drawer.flow.json \
  --execute \
  --record \
  --walkthrough \
  --out .kujo-agency-loop/lens/proof
```

Expected artifacts:

```text
.kujo-agency-loop/lens/proof/
  flow-steps.json
  walkthrough.html
  video/
    walkthrough.webm
    walkthrough.mp4    # optional when ffmpeg is available
  screenshots/
    promo-drawer-open.png
    promo-applied.png
```

Add it to the ledger:

```bash
runledger note "$RUN_ID" "Lens mobile flow passed and recorded proof walkthrough under .kujo-agency-loop/lens/proof."
```

The agency value: the fix is not just asserted. It is replayed in a browser and packaged as proof.

## Step 13: Explain The Diff With PatchBrief

Generate a reviewer-facing implementation brief:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/patchbrief/patchbrief.kujo" -- summarize \
  --format markdown \
  > .kujo-agency-loop/briefs/patchbrief.md
```

Generate suggested tests:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/patchbrief/patchbrief.kujo" -- suggest-tests \
  > .kujo-agency-loop/briefs/test-suggestions.md
```

Generate a handoff note:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/patchbrief/patchbrief.kujo" -- handoff \
  > .kujo-agency-loop/briefs/reviewer-handoff.md
```

The agency value: reviewers do not have to reverse-engineer the change from raw diff.

## Step 14: Measure Blast Radius With ChangeBucket

Run the ChangeBucket report:

```bash
changebucket --markdown \
  --output .kujo-agency-loop/briefs/changebucket.md
```

Run an enforced ChangeBucket check:

```bash
changebucket check \
  --max-files 8 \
  --max-churn 350 \
  --no-dependency-changes \
  --no-lockfile-changes \
  --no-generated-changes
```

If the ChangeBucket check fails, that does not automatically mean the implementation is wrong. It means the blast radius needs explanation.

Add it to the ledger:

```bash
runledger note "$RUN_ID" "ChangeBucket passed: scoped PHP/JS/CSS/test changes only, no dependency or lockfile changes."
```

The agency value: the client and reviewer can see the fix stayed small.

## Step 15: Optional Fence Architecture Check

For PHP/JS/CSS projects with a configured `fence.toml`, run:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/fence/fence.kujo" -- check \
  --changed-only \
  --format markdown \
  --output .kujo-agency-loop/briefs/fence.md
```

If the project does not yet have a `fence.toml`, skip this step or initialize a baseline separately. Do not add architecture rules casually in the same client bug-fix unless that is part of the task.

The agency value: architecture drift can be checked without relying on human memory.

## Step 16: Run ShipCheck Before Handoff

Run release-readiness scan:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/shipcheck/shipcheck.kujo" -- scan \
  --dir . \
  --format markdown \
  > .kujo-agency-loop/briefs/shipcheck.md
```

Run the gate:

```bash
"$KUJO_BIN" run "$KUJO_REPOS/shipcheck/shipcheck.kujo" -- gate \
  --dir . \
  --format json \
  > .kujo-agency-loop/briefs/shipcheck-gate.json
```

Add it to the ledger:

```bash
runledger note "$RUN_ID" "ShipCheck gate completed. Release-readiness report attached to client handoff."
```

The agency value: the final handoff includes release context, not just implementation details.

## Step 17: Finish The RunLedger Record

Record usage and cost if available:

```bash
runledger usage "$RUN_ID" --input 42000 --output 9000
runledger cost "$RUN_ID" --total 0.84 --currency USD
```

Finish the run:

```bash
runledger finish "$RUN_ID" \
  --status pass \
  --verdict "Mobile promo-code drawer fixed, deterministic checks passed, Lens walkthrough proof recorded, scoped ChangeBucket limits respected."
```

Generate a report:

```bash
runledger report \
  --task "Northstar mobile promo drawer fix" \
  --output .kujo-agency-loop/briefs/runledger-report.md
```

The agency value: the whole run has a final verdict with cost, usage, git state, and follow-ups.

## Step 18: Assemble The Client Handoff Packet

Create a client-facing summary:

```text
.kujo-agency-loop/client/
  CLIENT_HANDOFF.md
  mobile-promo-drawer.spec.md
  patchbrief.md
  changebucket.md
  eval-summary.json
  lens-walkthrough.html
  lens-recording.webm
  lens-recording.mp4
  shipcheck.md
  runledger-report.md
```

Example `CLIENT_HANDOFF.md`:

```markdown
# Northstar Outfitters: Mobile Promo Drawer Fix

## Summary

We fixed the mobile cart promo-code drawer so customers can reveal the promo input, enter `SAVE10`, apply it on the first tap, and continue checkout without the sticky checkout bar covering the form.

## Scope

Changed only the cart promo drawer behavior and supporting mobile layout. Promo-code validation rules and checkout payment behavior were not changed.

## Files Changed

- `public/cart.php`
- `assets/js/cart.js`
- `assets/css/cart.css`
- `tests/promo_code_test.php`

## Verification

- PHP promo-code regression tests passed.
- Cart JavaScript lint passed.
- Local cart page returned HTTP 200.
- Lens mobile browser flow passed.
- Lens recorded a step-by-step walkthrough and video proof.
- ChangeBucket confirmed a small scoped change with no dependency or lockfile changes.
- ShipCheck release-readiness gate completed.

## Browser Proof

- Walkthrough: `lens-walkthrough.html`
- Recording: `lens-recording.webm`
- Screenshots:
  - Promo drawer open
  - Promo code applied

## Review Notes

Please review the mobile CSS adjustment and confirm the sticky checkout bar spacing matches brand expectations. No promo-code business logic was intentionally changed.
```

Copy artifacts:

```bash
cp .kujo-agency-loop/spec/mobile-promo-drawer.md \
  .kujo-agency-loop/client/mobile-promo-drawer.spec.md

cp .kujo-agency-loop/briefs/patchbrief.md \
  .kujo-agency-loop/client/patchbrief.md

cp .kujo-agency-loop/briefs/changebucket.md \
  .kujo-agency-loop/client/changebucket.md

cp .kujo-agency-loop/eval/results/summary.json \
  .kujo-agency-loop/client/eval-summary.json

cp .kujo-agency-loop/lens/proof/walkthrough.html \
  .kujo-agency-loop/client/lens-walkthrough.html

if [ -f .kujo-agency-loop/lens/proof/video/walkthrough.webm ]; then
  cp .kujo-agency-loop/lens/proof/video/walkthrough.webm \
    .kujo-agency-loop/client/lens-recording.webm
fi

if [ -f .kujo-agency-loop/lens/proof/video/walkthrough.mp4 ]; then
  cp .kujo-agency-loop/lens/proof/video/walkthrough.mp4 \
    .kujo-agency-loop/client/lens-recording.mp4
fi

cp .kujo-agency-loop/briefs/shipcheck.md \
  .kujo-agency-loop/client/shipcheck.md

cp .kujo-agency-loop/briefs/runledger-report.md \
  .kujo-agency-loop/client/runledger-report.md
```

The agency value: the final delivery packet is understandable by a non-technical client and inspectable by a technical reviewer.

## Final Artifact Tree

By the end, the workflow has produced something like:

```text
.kujo-agency-loop/
  spec/
    mobile-promo-drawer.spec.yml
    mobile-promo-drawer.md
    agent-context.md
  scout/
    northstar-storefront-<timestamp>/
      README.md
      FILE_TREE.md
      AGENTS.md
      CHECKLIST.md
      intelligence.json
  scent/
    context.md
    context.json
    manifest.json
    redactions.json
  pack/
    MEGA_PROMPT.md
    agent/
      MASTER.md
      TODO.md
      HANDOFF.md
      DECISIONS.md
      REVIEW_CHECKLIST.md
      phases/
  eval/
    mobile-promo-drawer.eval.json
    results/
      summary.json
      artifact-manifest.json
      cli-summary.json
      eval-report.md
  lens/
    mobile-promo-drawer.flow.json
    check/
    inspect/
    proof/
      flow-steps.json
      walkthrough.html
      video/
        walkthrough.webm
        walkthrough.mp4
      screenshots/
  briefs/
    patchbrief.md
    test-suggestions.md
    reviewer-handoff.md
    changebucket.md
    fence.md
    shipcheck.md
    shipcheck-gate.json
    runledger-report.md
  client/
    CLIENT_HANDOFF.md
    mobile-promo-drawer.spec.md
    patchbrief.md
    changebucket.md
    eval-summary.json
    lens-walkthrough.html
    lens-recording.webm
    lens-recording.mp4
    shipcheck.md
    runledger-report.md
```

## What The Developer Sees

The developer sees a disciplined local workflow:

1. Client request becomes a Spec.
2. Repo context is discovered before editing.
3. Task context is bounded and redacted.
4. Agent execution is phase-based.
5. Every major event is logged.
6. Failures are captured reproducibly.
7. Checks are deterministic.
8. Browser proof is recorded.
9. The diff is explained.
10. Blast radius is measured.
11. Release readiness is checked.
12. The client gets a proof packet.

That is the utility: Kujo does not ask developers to trust the AI. It gives them a workflow for checking it.

## What The Client Sees

The client does not need to understand Spec, Eval, Scout, or Lens.

They see:

- The original issue was understood.
- The fix stayed in scope.
- The exact user flow was replayed.
- There is a video/walkthrough proving the promo-code path works.
- Tests passed.
- The change was small.
- The remaining review point is clear.

That is the agency story: not just faster work, but better proof.

## Demo Script For A Sales Or Developer Walkthrough

Use this as the narrative:

```text
1. "Here is the messy client request."
2. "First we turn it into a task contract so the agent cannot wander."
3. "Then Scout maps the repo and Scent builds only the context needed for this fix."
4. "PackWrite turns that into a phase-based implementation pack."
5. "RunLedger starts the audit trail before code changes happen."
6. "The implementation runs against the contract."
7. "Eval checks the mechanical acceptance criteria."
8. "Lens opens the real cart page on mobile and replays the exact customer flow."
9. "PatchBrief explains the diff, ChangeBucket shows the blast radius, and ShipCheck checks release readiness."
10. "Now we hand the client a proof packet: what changed, what passed, and a video walkthrough."
```

The one-sentence pitch:

> Kujo turns an AI-assisted bug fix into a client-verifiable delivery record.

## Current Manual Step vs Future Product Wrapper

Today, the workflow is a set of composable commands. That is good for transparency, but a lot to type.

A polished developer-facing wrapper could preserve the artifacts while reducing the command surface:

```bash
kujo agency-loop init "Fix mobile promo drawer" --repo .
kujo agency-loop context
kujo agency-loop start
kujo agency-loop verify
kujo agency-loop prove --url http://127.0.0.1:8080/cart.php --flow mobile-promo-drawer
kujo agency-loop handoff
```

Or one guided command:

```bash
kujo agency-loop run .kujo-agency-loop/spec/mobile-promo-drawer.spec.yml \
  --url http://127.0.0.1:8080/cart.php \
  --client "Northstar Outfitters"
```

The important part is not hiding the tools. The important part is making the path obvious.

## Checklist

Use this checklist when dogfooding the workflow:

- [ ] Spec validates.
- [ ] Spec renders to Markdown.
- [ ] Spec exports Eval suite.
- [ ] Scout repo map exists.
- [ ] Scent context pack exists and redactions were reviewed.
- [ ] PackWrite agent pack validates.
- [ ] RunLedger run started before implementation.
- [ ] Implementation notes were added to RunLedger.
- [ ] Any failed commands were captured with CaseFile.
- [ ] Eval suite passed.
- [ ] Lens read-only check passed.
- [ ] Lens inspect was used to avoid guessed selectors.
- [ ] Lens flow validated.
- [ ] Lens flow executed with recording and walkthrough.
- [ ] PatchBrief summary exists.
- [ ] ChangeBucket report exists and its bucket limits are acceptable.
- [ ] Fence check passed or was explicitly skipped.
- [ ] ShipCheck scan/gate completed.
- [ ] RunLedger was finished with a verdict.
- [ ] Client handoff packet was assembled.

## Why This Workflow Is Different

Most AI coding demos stop when code compiles.

This workflow stops when there is proof:

- proof of intent,
- proof of context,
- proof of scope,
- proof of checks,
- proof of browser behavior,
- proof of change size,
- proof of handoff.

That is why it fits agencies: the deliverable is not just a patch. The deliverable is confidence.
