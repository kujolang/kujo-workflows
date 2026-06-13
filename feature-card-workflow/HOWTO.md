# Feature Card Workflow HOWTO

This tutorial shows a developer how to run the Feature Card workflow against any local git repository.

The goal is simple:

```text
paste card -> run workflow -> agent implements -> Kujo tools verify -> Lens records proof -> review packet is ready
```

The workflow is local-first. It writes proof and review artifacts under the target repository:

```text
.kujo/feature-cards/<card-id>/
```

## 1. Prerequisites

Install or verify these tools before running the workflow.

### Required

- Git
- Bash
- Python 3
- Node.js and npm
- PHP and Composer for PHP/WordPress-style repos
- Codex CLI, used for the implementation agent
- Kujo runtime
- The sibling Kujo tool repos under:

```text
/Users/robertdevore/2026/Kujolang/kujo-repos/
```

Expected sibling repos include:

```text
kujo
spec
scout
scent
lens
eval
patchbrief
changebucket
shipcheck
runledger
kujo-workflows
```

### Verify Local Tools

Run:

```bash
git --version
python3 --version
node --version
npm --version
php --version
composer --version
/Applications/Codex.app/Contents/Resources/codex --version
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo --version
```

If your Kujo binary is somewhere else, set:

```bash
export KUJO_BIN="/path/to/kujo"
```

## 2. Prepare The Target Repo

Go to the repository you want the agent to work in:

```bash
cd /path/to/project-repo
git status --short
```

Start from a clean or understood working tree. The workflow will create/switch to a feature branch, but it will not protect you from unrelated local changes.

If the project has dependencies, install them first:

```bash
composer install
npm install
```

Use the commands appropriate for the project. For non-PHP or non-Node repos, use that repo's normal setup.

## 3. Start The Local Site

If the task needs browser proof, start the app/site locally before running the workflow.

Examples:

```bash
npm run dev
```

```bash
php -S 127.0.0.1:8888 -t public
```

Or use your local WordPress/dev environment.

Find the exact page where the bug or feature can be observed. This becomes `FEATURE_LENS_URL`.

Example:

```text
http://127.0.0.1:8888/repro-page/
```

## 4. Create The Card File

Create a markdown file in the target repo:

```bash
cat > card.md <<'EOF'
# CARD-123 Fix cache-related page jump

## Problem

Paste the real task/card details here.

## Desired Behavior

Describe what should happen after the fix.

## Acceptance Criteria

- The page no longer jumps after cached content loads.
- Existing cache behavior still works.
- Relevant PHP and JavaScript checks pass.
- Lens records pre/post browser proof.

## Verification Expectations

- Run the project test/build commands.
- Use Lens against the local page that reproduces the issue.
EOF
```

Use the real card ID from your task system when possible.

## 5. Run The Workflow

### Public / Logged-Out Page

Use this when the page can be viewed without logging in:

```bash
FEATURE_LENS_URL="http://127.0.0.1:8888/repro-page/" \
FEATURE_VERIFY_COMMANDS=$'composer validate --no-check-publish\nnpm test -- --watch=false\nnpm run build' \
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo-workflows/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh \
  CARD-123 \
  card.md \
  /path/to/project-repo
```

### Logged-In Page

Use this when the proof page needs an authenticated session. Use test-only credentials.

```bash
export TEST_SITE_USER="test-user@example.test"
export TEST_SITE_PASS="local-test-password"

FEATURE_LENS_URL="http://127.0.0.1:8888/my-account/" \
FEATURE_AUTH_MODE=login \
FEATURE_LOGIN_URL="http://127.0.0.1:8888/login/" \
FEATURE_LOGIN_USERNAME_ENV=TEST_SITE_USER \
FEATURE_LOGIN_PASSWORD_ENV=TEST_SITE_PASS \
FEATURE_LOGIN_SUCCESS_TEXT="My account" \
FEATURE_VERIFY_COMMANDS=$'composer validate --no-check-publish\nnpm test -- --watch=false\nnpm run build' \
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo-workflows/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh \
  CARD-123 \
  card.md \
  /path/to/project-repo
```

For WordPress-style login screens, the default selectors usually work. For other apps, override them:

```bash
FEATURE_LOGIN_USER_SELECTOR='input[name="email"]'
FEATURE_LOGIN_PASSWORD_SELECTOR='input[name="password"]'
FEATURE_LOGIN_SUBMIT_SELECTOR='button[type="submit"]'
FEATURE_LOGIN_SUCCESS_SELECTOR='main'
```

Do not paste real production credentials into `card.md`. Prefer `FEATURE_LOGIN_USERNAME_ENV` and `FEATURE_LOGIN_PASSWORD_ENV`.

## 6. What The Workflow Does

The workflow will:

1. Create or switch to `feature/<card-id>`.
2. Create `.kujo/feature-cards/<card-id>/`.
3. Add that run folder to `.git/info/exclude` so proof artifacts do not pollute git status.
4. Convert the card into a Spec.
5. Run Scout and Scent for repo/task context.
6. Start a RunLedger receipt.
7. Run pre-fix Lens inspect/check/flow when `FEATURE_LENS_URL` is set.
8. Run Codex non-interactively to implement the card.
9. Run `FEATURE_VERIFY_COMMANDS`, or conservative default checks when possible.
10. Run Eval if the agent creates an eval suite.
11. Run post-fix Lens check and recorded walkthrough.
12. Generate PatchBrief, ChangeBucket, ShipCheck, RunLedger, and reviewer handoff files.

The script exits nonzero if any stage fails. Even on failure, it writes the summary and handoff so you can inspect what happened.

## 7. Review The Output

Start here:

```bash
open .kujo/feature-cards/CARD-123/summary.md
```

Or inspect in the terminal:

```bash
sed -n '1,200p' .kujo/feature-cards/CARD-123/summary.md
cat .kujo/feature-cards/CARD-123/status.tsv
```

Important files:

```text
.kujo/feature-cards/CARD-123/summary.md
.kujo/feature-cards/CARD-123/status.tsv
.kujo/feature-cards/CARD-123/handoff/reviewer-handoff.md
.kujo/feature-cards/CARD-123/handoff/testing-request.md
.kujo/feature-cards/CARD-123/implementation/notes.md
.kujo/feature-cards/CARD-123/implementation/diff-stat.txt
.kujo/feature-cards/CARD-123/briefs/patchbrief.md
.kujo/feature-cards/CARD-123/briefs/changebucket.md
.kujo/feature-cards/CARD-123/briefs/shipcheck.md
.kujo/feature-cards/CARD-123/ledger/runledger-report.md
```

Lens proof:

```text
.kujo/feature-cards/CARD-123/lens/pre-fix/flow/walkthrough.html
.kujo/feature-cards/CARD-123/lens/proof/walkthrough.html
```

Open the walkthroughs in a browser and compare pre-fix vs post-fix behavior.

## 8. Review The Code

Check the final git diff:

```bash
git status --short
git diff --stat
git diff
```

Use PatchBrief as your first summary:

```bash
sed -n '1,200p' .kujo/feature-cards/CARD-123/briefs/patchbrief.md
```

Use ChangeBucket to understand blast radius:

```bash
sed -n '1,200p' .kujo/feature-cards/CARD-123/briefs/changebucket.md
```

Review any failed or skipped rows:

```bash
awk -F '\t' '$2 != "pass" { print }' .kujo/feature-cards/CARD-123/status.tsv
```

Open the matching log from the fourth column when something needs investigation.

## 9. Commit Locally

By default the workflow does not commit. After review, commit the intended code changes:

```bash
git status --short
git add <intended files>
git commit -m "CARD-123: fix cache-related page jump"
```

The `.kujo/feature-cards/CARD-123/` folder is excluded locally through `.git/info/exclude`, so it should not be committed unless your team explicitly wants selected proof artifacts tracked.

## 10. Optional Auto-Commit

If your team wants the workflow to commit automatically after running:

```bash
FEATURE_COMMIT=1 \
FEATURE_COMMIT_MESSAGE="CARD-123: fix cache-related page jump" \
FEATURE_LENS_URL="http://127.0.0.1:8888/repro-page/" \
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo-workflows/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh \
  CARD-123 \
  card.md \
  /path/to/project-repo
```

Still review the commit before pushing.

## 11. Optional Push

After reviewing the branch:

```bash
git status --short
git log --oneline -5
git push -u origin "$(git branch --show-current)"
```

Then paste the contents of:

```text
.kujo/feature-cards/CARD-123/handoff/testing-request.md
```

into the task card or pull request.

## 12. Troubleshooting

### Lens fails with exit code 3

Usually the local URL is not reachable, the local server is not running, or the page requires login.

Check:

```bash
curl -I "$FEATURE_LENS_URL"
```

### Login flow fails

Override selectors:

```bash
FEATURE_LOGIN_USER_SELECTOR='input[name="email"]'
FEATURE_LOGIN_PASSWORD_SELECTOR='input[name="password"]'
FEATURE_LOGIN_SUBMIT_SELECTOR='button[type="submit"]'
FEATURE_LOGIN_SUCCESS_TEXT='Dashboard'
```

### Verification commands fail

Open the log named in `status.tsv`.

Example:

```bash
cat .kujo/feature-cards/CARD-123/logs/verify-1.log
```

### ShipCheck fails in a small or unusual repo

Review the ShipCheck report:

```bash
sed -n '1,200p' .kujo/feature-cards/CARD-123/briefs/shipcheck.md
```

Some repos may not have release metadata yet. Treat that as a review signal, not necessarily a code failure.

## 13. Safety Notes

- Use test-only credentials.
- Do not put passwords in card files.
- Review Lens recordings before sharing externally.
- Keep generated run folders local unless your team decides otherwise.
- Start from a clean or understood working tree.
- Do not blindly push just because the workflow completed.

## Quick Reference

Unauthenticated:

```bash
FEATURE_LENS_URL="http://127.0.0.1:8888/repro-page/" \
FEATURE_VERIFY_COMMANDS=$'composer validate --no-check-publish\nnpm test -- --watch=false\nnpm run build' \
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo-workflows/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh CARD-123 card.md /path/to/project-repo
```

Authenticated:

```bash
export TEST_SITE_USER="test-user@example.test"
export TEST_SITE_PASS="local-test-password"

FEATURE_LENS_URL="http://127.0.0.1:8888/my-account/" \
FEATURE_AUTH_MODE=login \
FEATURE_LOGIN_URL="http://127.0.0.1:8888/login/" \
FEATURE_LOGIN_USERNAME_ENV=TEST_SITE_USER \
FEATURE_LOGIN_PASSWORD_ENV=TEST_SITE_PASS \
FEATURE_LOGIN_SUCCESS_TEXT="My account" \
FEATURE_VERIFY_COMMANDS=$'composer validate --no-check-publish\nnpm test -- --watch=false\nnpm run build' \
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo-workflows/feature-card-workflow/muzzle-template/workflows/feature-card-full.sh CARD-123 card.md /path/to/project-repo
```
