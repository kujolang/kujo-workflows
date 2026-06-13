# Agency Runner Build Goal

## Purpose

Build a universal, modular, decentralized, agent-focused workflow runner that turns the existing Kujo tool ecosystem into a seamless real-world agency development loop.

The runner should let a human kick off a task, provide or select a site profile, and then allow an agent to do the middle of the work:

- understand the task
- prepare the working documents
- authenticate into the target site when needed
- reproduce the bug or workflow problem
- capture failure proof
- inspect the codebase
- build an implementation plan
- apply the fix
- run deterministic checks
- run browser proof
- record the full ledger
- generate the final review packet

The human should not need to participate in the middle of the workflow unless a configured safety gate is triggered. The default experience should be:

```text
Human starts task
Agent performs the loop
Human reviews final logs/docs/artifacts
Human sends handoff to client, boss, reviewer, or QA
```

This is not a replacement for human accountability. It is a workflow system that removes repetitive setup, context gathering, proof generation, verification, logging, and handoff work from developers who handle many client tasks per week.

## Product Vision

The current Agency Verified Fix Loop demo proves that Kujo primitives can be chained together:

```text
Spec
Scout
Scent
PackWrite
RunLedger
Lens
CaseFile
Eval
PatchBrief
ChangeBucket
ShipCheck
```

The next step is to hide the orchestration complexity behind a clear runner:

```bash
kujo agency run
```

The workflow should feel like a task cockpit, not a pile of independent tools.

The runner should make real-world client work easy across WordPress, Drupal, Laravel, Shopify-style themes, PHP apps, static sites, custom CMS projects, and ordinary web applications.

It must work with logged-in flows such as:

- editing account settings
- submitting admin forms
- changing CMS content
- updating profile information
- testing checkout flows
- verifying gated pages
- reproducing customer-only bugs
- validating editor/admin dashboard behavior

The runner should be useful even when there is no CMS, no login, or no browser flow.

## Primary Outcome

Create an `agency` workflow runner that lets an agent complete real tasks from a human-readable task description and a reusable site profile.

The runner should produce a complete artifact bundle at the end of every task:

```text
.kujo/runs/<run-id>/
  summary.md
  task/
  spec/
  context/
  auth/
  reproduce/
  implementation/
  eval/
  lens/
  casefile/
  briefs/
  ledger/
  handoff/
  logs/
```

The final handoff should make it easy for a human reviewer to answer:

- What was the task?
- What was the initial failure?
- Was the failure actually reproduced?
- What files did the agent inspect?
- What files did the agent change?
- Why was the fix chosen?
- What checks ran?
- What browser proof exists?
- What risks remain?
- What should a human reviewer look at?
- Is the work safe to give to a client, boss, QA team, or reviewer?

## Core Principle

The flow is agent-focused.

Do not design for a human developer to perform the middle steps manually.

Bad default:

```text
Human pastes task
Human writes spec
Human logs into site
Human records flow
Human runs context tools
Human fixes code
Human runs evals
Human records proof
Human writes handoff
```

Correct default:

```text
Human pastes task
Human selects site/profile if needed
Agent prepares spec and plan
Agent logs into site using configured auth/session
Agent reproduces the issue
Agent captures proof
Agent inspects code
Agent applies fix
Agent verifies fix
Agent records proof
Agent prepares handoff
Human reviews final packet
```

The system may pause for a human only at explicit safety gates:

- production environment detected
- destructive action requested
- missing credentials or expired session
- ambiguous task target
- required external service unavailable
- irreversible database/content operation
- legal/security/financial risk
- configured approval checkpoint

## Command Shape

The initial CLI should be simple and composable.

Recommended commands:

```bash
kujo agency init
kujo agency site add
kujo agency site list
kujo agency site doctor
kujo agency login
kujo agency task
kujo agency run
kujo agency continue
kujo agency verify
kujo agency handoff
kujo agency status
kujo agency open
```

The system may initially be implemented as a wrapper script or standalone package before becoming a first-class Kujo command. The product behavior matters more than the first implementation location.

## Ideal Everyday Flow

For a site that has already been configured:

```bash
kujo agency task --site acme
```

The tool prompts:

```text
Paste the client task:
```

Human pastes:

```text
Users can update their display name in My Account, but after clicking Save
the success message appears and the value does not persist after refresh.
Please fix and provide proof using the staging test customer account.
```

The runner then:

1. creates a run id
2. writes the raw task to the run folder
3. creates or updates the Spec document
4. selects a recipe if one matches
5. checks the site profile
6. checks auth/session availability
7. starts RunLedger
8. runs Scout/Scent for relevant code context
9. creates an agent implementation pack
10. uses Lens to reproduce the issue
11. captures failure with CaseFile
12. has the agent apply the fix
13. runs deterministic Eval checks
14. runs logged-in Lens proof
15. runs PatchBrief, ChangeBucket, ShipCheck
16. finishes RunLedger
17. writes a final client/reviewer handoff packet

The human receives:

```text
Run complete.
Status: needs human review
Handoff: .kujo/runs/<run-id>/handoff/HANDOFF.md
Lens proof: .kujo/runs/<run-id>/lens/proof/walkthrough.html
Video proof: .kujo/runs/<run-id>/lens/proof/video/walkthrough.mp4
```

## Site Onboarding Flow

Site onboarding should happen once per project/site/environment, not once per task.

Command:

```bash
kujo agency site add acme
```

The wizard should collect:

- site name
- CMS/app type
- repo path
- environment type
- base URL
- login URL
- allowed user roles
- auth strategy
- test user requirements
- state reset strategy
- default browser viewport profiles
- safe file paths
- likely source roots
- excluded paths
- secret redaction rules
- task recipes available for the site

Example resulting file:

```yaml
version: 1
name: acme
type: wordpress
environment: staging
base_url: "https://staging.acme.example"
login_url: "https://staging.acme.example/wp-login.php"
repo_path: "/Users/dev/Sites/acme"

safety:
  allow_production: false
  require_clean_git: true
  require_test_user: true
  require_state_reset: false
  max_changed_files_default: 12
  max_churn_default: 600
  protected_paths:
    - "wp-config.php"
    - ".env"
    - "composer.lock"
    - "package-lock.json"

auth:
  default_role: customer
  roles:
    customer:
      strategy: saved-browser-session
      username_env: ACME_CUSTOMER_USERNAME
      password_env: ACME_CUSTOMER_PASSWORD
      session_file: ".kujo/agency/auth/acme/customer.storage-state.json"
    admin:
      strategy: saved-browser-session
      username_env: ACME_ADMIN_USERNAME
      password_env: ACME_ADMIN_PASSWORD
      session_file: ".kujo/agency/auth/acme/admin.storage-state.json"

source:
  roots:
    - "wp-content/themes/acme"
    - "wp-content/plugins/acme-membership"
  exclude:
    - "wp-content/uploads"
    - "node_modules"
    - "vendor"
    - ".git"

reset:
  before_each_run: ".kujo/agency/reset/before.sh"
  after_each_run: ".kujo/agency/reset/after.sh"

recipes:
  - account-settings
  - contact-form
  - admin-editor
  - checkout

redactions:
  env:
    - ACME_CUSTOMER_PASSWORD
    - ACME_ADMIN_PASSWORD
  patterns:
    - "wordpress_logged_in_[^=]+=[^;]+"
    - "wp-settings-[^=]+=[^;]+"
    - "nonce=[A-Za-z0-9_-]+"
```

## Auth Requirements

Logged-in workflows must be first-class.

The runner should support these auth strategies:

- no auth
- saved browser session
- username/password login flow
- cookie injection
- custom login command
- manual one-time login followed by saved session

For the first implementation, prioritize saved browser session and username/password login flow.

Command:

```bash
kujo agency login --site acme --role customer
```

Expected behavior:

1. opens the login URL in Lens/browser automation
2. fills credentials from env vars when available
3. allows manual login fallback when configured
4. verifies login succeeded using a selector or URL pattern
5. saves browser storage state
6. writes an auth health artifact
7. redacts credentials and sensitive cookies from logs

The runner must never write raw passwords into:

- run logs
- Lens output
- CaseFile output
- RunLedger notes
- handoff documents
- generated specs
- terminal summaries

If credentials are missing, the agent should stop and report exactly which env vars are required.

## Task Recipes

Recipes make common agency tasks fast.

A recipe is a reusable description of:

- likely URLs
- likely selectors
- common assertions
- likely source roots
- suggested eval checks
- Lens flow skeletons
- data setup/reset needs
- safety rules

Initial recipe set:

- `account-settings`
- `contact-form`
- `admin-editor`
- `checkout`
- `login-registration`
- `search-filter`
- `theme-layout`
- `email-notification`
- `plugin-integration`
- `performance-regression`

Example recipe:

```yaml
version: 1
id: account-settings
name: Account Settings Persistence
description: Verify logged-in users can update and persist account/profile fields.

requires:
  auth: true
  role: customer

flow:
  entry_path: "/my-account/"
  actions:
    - locate account settings page
    - capture current value
    - change value to run-specific test value
    - save
    - verify success message
    - refresh
    - verify changed value persisted

assertions:
  - no browser console errors
  - no 5xx network responses
  - success message appears
  - updated value persists after refresh

likely_files:
  wordpress:
    - "wp-content/themes/*"
    - "wp-content/plugins/*account*"
    - "wp-content/plugins/*member*"
  drupal:
    - "web/modules/custom"
    - "web/themes/custom"

eval_suggestions:
  - php syntax checks
  - unit tests when present
  - changed-file grep for unsafe debug output
  - HTTP status check for account page
```

Recipes must be overrideable per site and per task.

## Task Intake

The task intake should accept several input styles:

```bash
kujo agency task --site acme
kujo agency task --site acme --file task.md
kujo agency task --site acme --recipe account-settings
kujo agency task --site acme --url https://ticket-system.example/TICKET-123
```

The runner should preserve the original task exactly.

It should create:

```text
.kujo/runs/<run-id>/task/raw.md
.kujo/runs/<run-id>/task/normalized.md
.kujo/runs/<run-id>/task/questions.md
.kujo/runs/<run-id>/task/assumptions.md
```

The agent should infer:

- likely task type
- required auth role
- relevant URLs
- relevant source roots
- expected user-visible behavior
- likely acceptance criteria
- risk level
- whether a browser reproduction is required

The agent should ask the human for input only if it cannot safely proceed.

## Spec Generation

The runner should use Spec to generate a structured task contract from the raw task, site profile, recipe, and any inferred details.

Spec output should include:

- goal
- background
- scope
- non-goals
- relevant systems
- likely files
- acceptance criteria
- eval requirements
- browser proof requirements
- auth requirements
- safety rules
- risks
- human review expectations

The Spec should be written to:

```text
.kujo/runs/<run-id>/spec/task.spec.yml
.kujo/runs/<run-id>/spec/task.spec.md
.kujo/runs/<run-id>/spec/agent-context.md
```

The agent should not rely on the Spec being perfect. It should treat it as the working contract and update or annotate it if reproduction reveals different facts.

## Context Gathering

The runner should gather context automatically.

Use Scout for broad repo mapping:

```text
.kujo/runs/<run-id>/context/scout/
```

Use Scent for task-specific context:

```text
.kujo/runs/<run-id>/context/scent/
```

The context pack should include:

- site profile
- raw task
- normalized task
- Spec agent context
- selected recipe
- relevant file list
- repo map
- framework/CMS hints
- redaction rules
- safety rules
- reproduction flow
- eval plan

The system should bias toward small, relevant context packs, not dumping the whole repo.

## Agent Implementation Pack

The runner should create an implementation pack for the coding agent.

The pack should be written to:

```text
.kujo/runs/<run-id>/implementation/agent-pack/
```

It should include:

- `MASTER.md`
- `TODO.md`
- `HANDOFF.md`
- `DECISIONS.md`
- `REVIEW_CHECKLIST.md`
- phase files
- reproduction findings
- failure proof links
- relevant code context
- safety constraints
- exact verification commands

The implementation instructions must be agent-first:

```text
You are expected to complete the fix unless blocked by a safety gate.
Do not stop after analysis.
Do not ask the human to perform middle steps.
Apply the smallest safe fix.
Run verification.
Produce handoff artifacts.
```

Avoid wording such as `dev/agent fix`.

The implementation phase is:

```text
agent fix
```

## Reproduction Phase

The runner should try to reproduce the problem before any code changes.

For browser tasks:

1. prepare/reset state
2. authenticate if required
3. open target page
4. perform the reported user actions
5. capture screenshots
6. capture console/network data
7. detect failure according to recipe/task assertions
8. write a reproduction report

Outputs:

```text
.kujo/runs/<run-id>/reproduce/report.md
.kujo/runs/<run-id>/reproduce/result.json
.kujo/runs/<run-id>/lens/pre-fix/
.kujo/runs/<run-id>/casefile/pre-fix/
```

If the bug cannot be reproduced, the runner should not blindly continue to code changes. It should classify the result:

- not reproduced
- environment unavailable
- auth failure
- selector drift
- task ambiguity
- intermittent
- reproduced with modified steps

If configured, the runner may still proceed to inspect and suggest likely fixes, but the default should be to stop before modification when reproduction is impossible.

## Agent Fix Phase

The agent should perform the fix using the implementation pack.

Required behavior:

- inspect relevant files before editing
- preserve unrelated user changes
- keep changes scoped
- prefer the smallest fix that satisfies acceptance criteria
- avoid dependency changes unless explicitly justified
- avoid broad refactors
- avoid hidden generated changes
- update tests when appropriate
- update docs only if relevant
- record decisions

The runner should capture:

```text
.kujo/runs/<run-id>/implementation/changed-files.txt
.kujo/runs/<run-id>/implementation/decision-log.md
.kujo/runs/<run-id>/implementation/agent-transcript.md
```

The system should support multiple implementation backends later, but the workflow contract should not depend on a specific model/provider.

## Verification Phase

Verification must combine deterministic checks and browser proof.

Use Eval for deterministic checks:

```text
.kujo/runs/<run-id>/eval/
```

Checks may include:

- unit tests
- integration tests
- syntax checks
- build checks
- lint checks
- HTTP status checks
- file-content checks
- changed-file policy checks
- CMS CLI checks
- database read checks when safe

Use Lens for browser proof:

```text
.kujo/runs/<run-id>/lens/proof/
```

Browser proof should include:

- screenshots
- console logs
- network logs
- step report
- walkthrough HTML
- optional video recording

For logged-in flows, Lens proof must confirm:

- user is logged in as the expected role
- target workflow can be performed
- final state matches acceptance criteria
- state persists after refresh when persistence is part of the task
- no unexpected console errors occurred

## Artifact and Handoff Phase

The final handoff should be written to:

```text
.kujo/runs/<run-id>/handoff/HANDOFF.md
```

It should include:

- task summary
- environment
- site profile
- auth role used
- reproduction result
- fix summary
- changed files
- verification summary
- Lens proof links
- Eval results
- PatchBrief summary
- ChangeBucket report
- ShipCheck result
- RunLedger link/report
- residual risks
- reviewer checklist
- client-safe summary

Also create a client-safe packet:

```text
.kujo/runs/<run-id>/handoff/client/
  CLIENT_SUMMARY.md
  PROOF_LINKS.md
  lens-walkthrough.html
  lens-recording.mp4
  eval-summary.json
  patchbrief.md
  changebucket.md
  shipcheck.md
  runledger-report.md
```

The client-safe packet must not include:

- secrets
- passwords
- raw cookies
- private environment files
- internal-only notes unless explicitly marked safe
- unrelated repo context
- sensitive customer/user data

## RunLedger Requirements

Every task run should create a RunLedger entry.

The ledger should record:

- task start
- selected site/profile
- selected recipe
- auth role
- reproduction result
- agent fix start
- key implementation notes
- eval results
- Lens proof result
- costs/usage if available
- final verdict

RunLedger should produce:

```text
.kujo/runs/<run-id>/ledger/run.json
.kujo/runs/<run-id>/ledger/report.md
```

The final status should be one of:

- pass
- needs-review
- blocked
- failed-verification
- failed-reproduction
- unsafe-to-proceed

## PatchBrief, ChangeBucket, and ShipCheck Requirements

PatchBrief should summarize the diff for reviewers.

ChangeBucket should enforce blast-radius constraints:

- max changed files
- max churn
- no dependency changes unless allowed
- no lockfile changes unless allowed
- no generated changes unless allowed

ShipCheck should run release safety checks:

- obvious secrets
- debug output
- temporary files
- risky environment changes
- generated artifact leakage

Outputs:

```text
.kujo/runs/<run-id>/briefs/patchbrief.md
.kujo/runs/<run-id>/briefs/changebucket.md
.kujo/runs/<run-id>/briefs/shipcheck.md
```

## Decentralized Design

The runner should not require a hosted service.

Everything needed for a task run should live in:

- the local repo
- `.kujo/agency/`
- `.kujo/runs/`
- environment variables
- optional local credential/session storage

Do not design around a central database.

Do not require a hosted dashboard for the first version.

The output should be portable:

- zipped and sent to a client
- attached to a ticket
- reviewed in a PR
- archived with project records
- consumed by another agent

## Modularity Requirements

The runner should be modular.

Each phase should have a clear contract:

```text
intake
site-profile
auth
state-reset
spec
context
reproduce
agent-fix
verify
proof
briefs
ledger
handoff
```

Each phase should be independently rerunnable when possible.

Examples:

```bash
kujo agency run --phase reproduce --run <run-id>
kujo agency run --phase verify --run <run-id>
kujo agency handoff --run <run-id>
kujo agency continue --run <run-id>
```

The runner should write machine-readable phase status:

```json
{
  "run_id": "2026-06-11-acme-account-settings-001",
  "status": "needs-review",
  "phases": {
    "intake": "pass",
    "auth": "pass",
    "reproduce": "pass",
    "agent_fix": "pass",
    "verify": "pass",
    "handoff": "pass"
  }
}
```

## Resume and Failure Semantics

The runner must be resumable.

If a run fails halfway through, the human or another agent should be able to continue:

```bash
kujo agency continue --run <run-id>
```

The runner should not hide failures.

It should classify failures clearly:

- preflight failed
- site profile invalid
- auth failed
- state reset failed
- reproduction failed
- reproduction not possible
- agent fix failed
- eval failed
- browser proof failed
- safety gate triggered
- handoff generation failed

Each failure should write:

```text
.kujo/runs/<run-id>/errors/<phase>.md
.kujo/runs/<run-id>/errors/<phase>.json
```

The error report should include:

- command attempted
- exit code
- relevant log file
- likely cause
- next recommended action
- whether the run is safe to continue

## Safety Requirements

Default safety posture:

- staging only
- test users only
- no destructive operations without explicit approval
- no production unless `allow_production: true`
- no secret leakage
- no unbounded crawling
- no uncontrolled form submissions
- no payment capture
- no external email/SMS sends unless explicitly allowed
- no database writes outside configured reset/task scope

If the URL appears to be production and the profile says production is not allowed, stop.

If the flow includes checkout/payment, require a test payment mode marker.

If the flow includes user data, redact sensitive values.

If the flow includes admin actions, require an admin role profile and explicit recipe.

## Redaction Requirements

Redaction must be built in from the start.

Redact:

- passwords
- cookies
- auth headers
- nonces
- API keys
- CSRF tokens
- session ids
- email addresses when configured
- phone numbers when configured
- customer names when configured
- payment data

Redaction should apply to:

- logs
- Lens artifacts
- CaseFile artifacts
- RunLedger notes
- handoff files
- error reports

When data is redacted, preserve useful structure:

```text
customer@example.com -> [REDACTED_EMAIL]
wordpress_logged_in_xxx=abc123 -> wordpress_logged_in_[REDACTED]=[REDACTED_COOKIE]
```

## First Implementation Scope

Build a first usable version, not a perfect universal system.

Minimum viable feature set:

1. site profile schema
2. run folder creation
3. task intake from pasted text or file
4. recipe selection or manual recipe override
5. saved browser session auth
6. Spec generation from task/profile/recipe
7. Scout/Scent context generation
8. pre-fix Lens reproduction
9. CaseFile capture for failed reproduction
10. agent implementation pack generation
11. agent fix phase handoff contract
12. Eval execution
13. post-fix Lens proof
14. PatchBrief/ChangeBucket/ShipCheck
15. RunLedger tracking
16. final handoff generation
17. resume/status support

The first version may use shell scripts plus Kujo scripts if that is fastest, but the contracts and folder structure should be designed so it can become a first-class CLI command later.

## Suggested Repository Structure

Add a new project or folder:

```text
agency-runner/
  README.md
  bin/
    agency-loop
  docs/
    GOAL.md
    SITE_PROFILE.md
    RECIPES.md
    AUTH.md
    ARTIFACTS.md
  schemas/
    site-profile.schema.json
    recipe.schema.json
    run-state.schema.json
  recipes/
    account-settings.yml
    contact-form.yml
    admin-editor.yml
    checkout.yml
    theme-layout.yml
  templates/
    spec.yml.tpl
    eval.json.tpl
    handoff.md.tpl
    agent-pack/
      MASTER.md
      TODO.md
      HANDOFF.md
      DECISIONS.md
      REVIEW_CHECKLIST.md
  scripts/
    init-site.sh
    login.sh
    run-task.sh
    reproduce.sh
    verify.sh
    handoff.sh
  examples/
    wordpress-account-settings/
    drupal-contact-form/
```

If implemented inside an existing Kujo repo, preserve the same conceptual structure.

## Example End-to-End Real Task

Task:

```text
Users can update their display name in My Account, but after clicking Save
the success message appears and the value does not persist after refresh.
Please fix this on staging and provide proof using the test customer account.
```

Expected behavior:

```bash
kujo agency run --site acme --recipe account-settings --task task.md
```

The runner should:

1. create run id
2. load `acme` site profile
3. verify staging URL
4. verify customer saved session
5. start RunLedger
6. create Spec
7. gather context
8. open account settings page as customer
9. record current display name
10. change display name to run-specific value
11. save
12. refresh
13. detect old value returns
14. capture failure proof
15. inspect likely WordPress files
16. identify save handler issue
17. apply scoped fix
18. run PHP syntax/tests/build checks
19. rerun logged-in browser proof
20. verify new value persists after refresh
21. generate PatchBrief
22. enforce ChangeBucket
23. run ShipCheck
24. finish RunLedger
25. assemble handoff

Final status:

```text
needs-review
```

The status is `needs-review`, not `done`, because a human must review before client delivery.

## Human Review Contract

At the end, the human should only need to review:

- final handoff
- changed files
- Lens walkthrough/video
- Eval summary
- PatchBrief
- ChangeBucket
- ShipCheck
- RunLedger report
- residual risks

The runner should explicitly say:

```text
This run is ready for human review.
No unexpected verification failures were found.
```

Or:

```text
This run is not ready for delivery.
Verification failed in phase: lens-proof.
See: .kujo/runs/<run-id>/errors/lens-proof.md
```

## Acceptance Criteria

The build is successful when:

- A new site can be onboarded with a profile.
- A saved login session can be created for a role.
- A real task can be started from pasted text or a file.
- A run folder is created with a stable structure.
- Spec artifacts are generated.
- Scout/Scent context artifacts are generated.
- Lens can run a logged-in pre-fix reproduction flow.
- CaseFile can capture the pre-fix failure.
- An agent implementation pack is generated.
- The agent fix phase is clearly documented and executable.
- Eval can run deterministic verification.
- Lens can run logged-in proof after the fix.
- PatchBrief, ChangeBucket, and ShipCheck run after changes.
- RunLedger tracks the run.
- A final human-review handoff is generated.
- Secrets are not present in generated handoff artifacts.
- The run can be resumed after an interrupted phase.
- The workflow works without assuming a fictional fixture.

## Non-Goals For First Version

Do not build these first:

- hosted SaaS dashboard
- team permissions system
- cloud artifact storage
- full ticket-system integration
- perfect CMS auto-detection
- perfect selector generation
- multi-agent swarm management
- production deployment automation
- automatic PR creation unless already easy and safe

The first version should prove that one human can point the runner at a real repo/site/task and get an end-to-end agent-completed proof packet.

## Important Design Notes

The runner should make easy things easy, but not fake certainty.

If reproduction cannot be done, say so.

If auth fails, say so.

If the site is production, stop unless explicitly allowed.

If the agent changes too much, fail ChangeBucket.

If browser proof fails, do not produce a green handoff.

If the task is ambiguous, ask the smallest possible clarifying question.

If the task is safe and clear, proceed without asking the human to perform intermediate work.

## Implementation Priority

Recommended order:

1. Define run folder contract.
2. Define site profile schema.
3. Define recipe schema.
4. Build `site add` minimal wizard.
5. Build `login` saved-session command.
6. Build `task` intake command.
7. Build `run` orchestration command with phase tracking.
8. Add Spec generation.
9. Add Scout/Scent integration.
10. Add Lens pre-fix reproduction.
11. Add CaseFile failure capture.
12. Add agent-pack generation.
13. Add agent fix phase contract.
14. Add Eval integration.
15. Add Lens post-fix proof.
16. Add PatchBrief/ChangeBucket/ShipCheck.
17. Add RunLedger.
18. Add final handoff.
19. Add resume/status/open commands.
20. Add examples for WordPress and Drupal.

## Final Deliverable

The agent assigned to this goal should deliver:

- working runner prototype
- docs
- schemas
- default recipes
- at least one CMS-style example profile
- a complete example run using a logged-in browser flow
- generated artifact bundle
- known limitations
- next-step recommendations

The deliverable should make it clear how this becomes a top-tier workflow for agency developers who complete many small-to-medium client tasks each week.

The goal is not to show that Kujo can run many tools.

The goal is to show that Kujo can turn messy real-world client tasks into a reliable, agent-executed, proof-backed delivery workflow.
