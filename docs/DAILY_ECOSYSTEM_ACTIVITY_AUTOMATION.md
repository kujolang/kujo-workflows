# Daily Ecosystem Activity Automation

Reviewed against the local Strata `0.6.0` source, CLI, HTTP API, and current local data on 2026-07-16. All investigation commands were read-only. No Strata note, repository state, branch, remote, or RepoRadar registry record was changed.

## 1. Strata CLI findings

### Canonical executable and runtime

The canonical source-checkout invocation is:

```bash
cd /Users/robertdevore/2026/strata
npm run strata -- <command> [options]
```

`package.json` maps that command to `tsx app/cli/index.ts`. The CLI is an HTTP client; it never reads or writes SQLite directly. The desktop app owns the local SQLite database under Electron `userData` (currently `/Users/robertdevore/Library/Application Support/strata/data/strata.sqlite`) and starts the HTTP service. Automations must not use that database path directly.

The default endpoint is `http://127.0.0.1:3939`. Strata must already be running. The supported runtime settings are:

| Setting | Default | Purpose |
| --- | --- | --- |
| `STRATA_API_BASE_URL` | `http://127.0.0.1:3939` | Local HTTP endpoint |
| `STRATA_API_TOKEN` | unset | Optional API token; value is never printed by the CLI |
| `STRATA_CLI_OUTPUT` | `pretty` | `pretty` or `json` |
| `STRATA_CLI_DRY_RUN` | `false` | Default dry-run behavior |
| `STRATA_CLI_AGENT_MODE` | `false` | JSON-first, non-interactive agent behavior |
| `STRATA_CLI_TIMEOUT_MS` | `15000` in source | HTTP timeout override |

Equivalent global flags include `--base-url`, `--token`, `--json`, `--pretty`, `--quiet`, `--verbose`, `--dry-run`, `--confirm`, `--timeout`, `--agent`, `--no-color`, and `--fail-on-warning`. Prefer environment-based token handling so credentials do not appear in process arguments or reports.

Useful exit codes are `0` success, `2` validation error, `3` API unavailable, `4` authentication failure, `5` not found, `6` unsafe operation refused, `8` timeout, and `9` partial failure. JSON errors have `ok: false` and an `error` object with `code`, `message`, and optional `hint`/`details`.

### Tested read-only commands

These commands were run successfully against the local service:

```bash
cd /Users/robertdevore/2026/strata
npm run strata -- health --json
npm run strata -- config show --json
npm run strata -- config doctor --json
npm run strata -- projects list --json
npm run strata -- notes list --limit 500 --json
npm run strata -- tags list --json
```

Observed health was successful at `http://127.0.0.1:3939`, without token authentication. `config doctor` confirmed the API, localhost endpoint, repository context, and legacy helper script.

The following are also safe read operations:

```bash
npm run strata -- notes get <NOTE_UUID> --json
npm run strata -- notes get <NOTE_UUID> --content-only --pretty
npm run strata -- search "exact phrase" --limit 100 --json
```

`notes get` returns the full body. `notes list` and `search` also return full note objects, not summaries.

Do not use `agent context search` in Strata 0.6.0. Direct testing showed that the current Commander registration (`command('context search <query>')`) is parsed as a `context` command with positional arguments named `search` and `query`; the action receives the literal word `search` instead of the supplied phrase. Its JSON response reported `query: "search"` and returned unrelated recent notes. Generic `search <query>` is the reliable read-side command until this registration is fixed.

### Record model and filters

The public note object is:

```json
{
  "id": "uuid",
  "content": "# Markdown title\n\nBody",
  "createdAt": "2026-07-16T22:39:39.357Z",
  "updatedAt": "2026-07-16T22:39:39.357Z",
  "starred": false,
  "archived": false,
  "tags": ["agent", "summary"],
  "projectId": "uuid-or-null",
  "deletedAt": null
}
```

Projects are separate objects with `id`, `name`, `createdAt`, `updatedAt`, and `sortOrder`. The current projects are `Kujo`, `UpdraftCentral`, and `Agent Notes`; almost all recent agent records are correctly stored in `Agent Notes` while their real project/repository scope is encoded in Markdown and tags.

`notes list` supports only:

- `--query <substring>` across content, serialized tags, or project name
- `--tag <exact-tag>`
- `--project <name>` or `--project-id <uuid>`
- `--starred`
- `--archived true|false`
- `--include-deleted`
- `--limit <1..500>`

`search` supports query, tag, project, and limit. Search is SQL `LIKE` substring matching ordered by `updatedAt`; it is not semantic search despite the broader memory workflow language.

There are no first-class filters for created time, updated time, rolling windows, time zone, repository, agent, task, chat/session, note type, status, source, or consolidation state. Those concepts exist only when agents place them in the Markdown body or tags such as `repo-watchdog`, `memory-state-snapshot`, `status-active`, and `session-...`.

There are no native report or daily-digest commands. The intended `agent context search` wrapper is currently broken as described above, and `agent summary` creates a note, so neither belongs in this read-only automation. Backlinks and related-note endpoints can enrich a selected cluster, but relationships are otherwise usually searchable Markdown IDs rather than typed API fields.

### Output, limits, and complete-window retrieval

The CLI provides JSON and pretty text/table output. It does not provide JSONL or Markdown output.

There is no pagination or cursor support. This is important:

- `GET /notes` returns the complete non-deleted result set, ordered by `updatedAt` descending.
- The CLI then truncates `notes list` locally to at most 500 records.
- `GET /search` caps results at 100 at the HTTP layer, even though some CLI validation permits a larger number.
- The current database had 6,126 non-deleted notes, so `notes list --limit 500` is not a complete source.

Therefore the reliable daily process is: use the CLI for health/config validation, use authenticated `GET /notes` for a complete read, and filter both `createdAt` and `updatedAt` locally against one exact UTC interval. The endpoint has no server-side date filter, so the automation must temporarily hold all returned notes and must never print all bodies.

A token-safe complete read can be performed with Node's built-in `fetch`, reading the token only from the environment:

```bash
node --input-type=module - "$STRATA_API_BASE_URL" "$TMPDIR/strata-all.json" <<'NODE'
import fs from 'node:fs'
const [baseUrl, output] = process.argv.slice(2)
const headers = {}
if (process.env.STRATA_API_TOKEN) headers.Authorization = `Bearer ${process.env.STRATA_API_TOKEN}`
const response = await fetch(`${baseUrl.replace(/\/$/, '')}/notes`, { headers })
if (!response.ok) throw new Error(`Strata GET /notes failed: HTTP ${response.status}`)
const payload = await response.json()
if (!payload || !Array.isArray(payload.notes)) throw new Error('Unexpected Strata /notes response')
fs.writeFileSync(output, JSON.stringify(payload))
NODE
```

The current implementation accepts either `Authorization: Bearer` or `X-Strata-Token`. The service is intended to remain on localhost. When health fails, the automation should record `Strata unavailable`, preserve exit code/error category, skip narrative claims that require Strata, and continue with repository evidence.

### Commands to prohibit

The automation must never invoke `notes create`, `notes update`, `notes delete`, `notes delete-many`, `notes archive`, `notes unarchive`, `notes star`, `notes unstar`, any `agent capture|decision|todo|summary`, project create/rename/delete/reorder/import, or `POST /ai-edits/:id/revert`. `--dry-run` is unnecessary because the automation should use only GET/read commands.

## 2. Data-quality assessment

### Current sample

For the representative rolling window `2026-07-15T18:40:25-04:00` through `2026-07-16T18:40:25-04:00` (`2026-07-15T22:40:25Z` through `2026-07-16T22:40:25Z`):

- 131 notes were created or updated.
- 127 were newly created and four older notes were updated in the window.
- 129 were in `Agent Notes`; two were unprojected personal/tool notes and should not be treated as ecosystem work.
- 49 looked like session summaries/handoffs, 22 like state snapshots, six decisions, nine lessons, four constraints, and the rest a mixture of concise captures, corrections, procedures, personal notes, and legacy shapes.
- 100/131 had an identifiable repository field by conservative Markdown matching, 89 had a branch field, 124 contained a commit-like hash, 87 mentioned tests/validation, 74 mentioned push/synchronization, 96 contained a session/chat/run identifier, and 53 contained a next-step/open-work cue.

These are heuristic counts because Strata does not type these fields. They demonstrate that recent agent notes are generally rich enough for a digest, but not uniformly machine-readable.

### Strengths

Recent structured session memories often contain goal/intent, work completed, repositories and paths, branches, commit hashes, files, validation, push status, risks, open commitments, session IDs, and retrieval cues. Atomic memories commonly add authority, confidence, status, scope, evidence, and supersession relationships. This is sufficient to recover the narrative and verify many claims.

### Weaknesses and duplication patterns

- One task often produces a session handoff plus one or more state snapshots, decisions, lessons, corrections, and terse implementation captures. Counting notes counts the same work repeatedly.
- Legacy notes use several incompatible shapes: full session templates, bullet handoffs, dense single paragraphs, escaped literal `\n` text, and title-only placeholders.
- Repository scope may be an absolute path, slug, tag, multiple repositories in prose, or absent.
- Commit hashes are sometimes complete evidence sets and sometimes only the final commits in a longer series.
- Completion wording may describe a claim, a corrected state, a planned direction, a failed attempt, or a superseded state. The automation must not flatten those into “completed.”
- Some old notes were updated only to append supersession metadata. They belong in the time window as a state-change event, but their original work did not occur in the window.
- Tag quality is noisy: there were 1,718 distinct tags globally, including generic and auto-suggested terms. Tags are evidence, not a reliable ontology.
- Personal records and command notebooks can be updated in the same window. Project/tag/repository evidence is required before including them.
- Multi-repository tasks are common. A single ecosystem-wide accomplishment can correspond to many commits across many repositories.

### Defensible consolidation strategy

1. Select records where either `createdAt` or `updatedAt` is inside the exact window. Preserve which condition matched.
2. Exclude deleted records. Keep archived/superseded records only to explain an in-window supersession, correction, or archival event.
3. Classify each note from explicit body fields and tags: session/handoff, state snapshot, decision, correction, constraint, procedure, lesson, TODO/commitment, plan/research, implementation capture, or unrelated.
4. Extract stable keys in this order: explicit memory/session/chat/run/task/issue IDs; claimed commit hashes; absolute repository paths; repo tags/slugs; branch; distinctive artifact/file paths; normalized title/goal.
5. Cluster records sharing a session/task ID, overlapping commit set, same repository set plus near-identical goal, explicit `derived-from`/`learned-from`/`supersedes` relation, or a close creation interval with the same evidence.
6. Within a cluster, prefer the newest non-superseded state snapshot or final session handoff as the narrative anchor. Use atomic decisions/lessons/corrections as supporting facets, not extra accomplishments.
7. Split one large session into multiple accomplishments only when it has distinct outcomes, repository/evidence sets, or one code and one non-code result. Do not split by commit count.
8. Keep plans, failed attempts, blocked states, and research as separate non-completion outcomes. A later verified completion may subsume earlier progress, but retain unresolved limitations.
9. Collapse mechanical cross-repository campaigns by shared commit subjects, timestamps, and file patterns into one ecosystem accomplishment. The sample's 120 repeated tool-artifact commits across 40 repositories are one hygiene campaign, not 120 accomplishments.
10. Treat terse duplicate captures from multiple agents as corroboration only when their evidence agrees. If claims conflict, keep one discrepancy item and lower confidence.

### Recommended future note minimum

Every completion/handoff should include: absolute repository path(s); project; task/session ID; branch; exact commit hashes; current push/upstream state; concise intent; work performed; validation commands/results; completion status; open work; source artifacts; and whether changes were generated/mechanical. Non-code work should explicitly say `Repository evidence: not applicable` and name its durable artifact or decision source.

## 3. Recommended architecture

The strongest available model is:

1. **Strata — narrative and intent.** Complete `/notes` read, exact time-window filter, structured extraction, deduplication, and status/supersession handling.
2. **Repository inventory — discovery and omission coverage.** Explicit note paths first; RepoRadar's read-only `GET /api/repos` second; configured roots/paths third; bounded filesystem discovery only as a fallback.
3. **Git — technical verification.** Fresh read-only inspection of each relevant repository. RepoRadar status snapshots are not verification because they may be stale.

Strata does not maintain a canonical repository inventory. RepoRadar adds real value because its running `GET http://127.0.0.1:8080/api/repos` returned 84 tracked, non-archived entries with canonical paths and useful group/tag metadata. Its CLI `list` is human text only; `export` writes `reporadar-export.json` and must be avoided in read-only automation. RepoRadar's `scan` and `scan-all` update its SQLite history and must also be avoided. The API currently omits archived repositories and had seven tracked paths that were no longer Git worktrees, so every returned path must be validated.

Use RepoRadar only as a path inventory. Its snapshot fields (`is_clean`, ahead/behind, last commit) are advisory and can be hours old. Run fresh Git reads for the report.

### Exact reporting window

Use one 86,400-second rolling window and render both local and UTC bounds. On macOS:

```bash
REPORT_TZ=America/Toronto
WINDOW_HOURS=24
end_epoch=$(date +%s)
start_epoch=$((end_epoch - WINDOW_HOURS * 3600))
START_LOCAL=$(TZ="$REPORT_TZ" date -r "$start_epoch" '+%Y-%m-%dT%H:%M:%S%z')
END_LOCAL=$(TZ="$REPORT_TZ" date -r "$end_epoch" '+%Y-%m-%dT%H:%M:%S%z')
START_UTC=$(date -u -r "$start_epoch" '+%Y-%m-%dT%H:%M:%SZ')
END_UTC=$(date -u -r "$end_epoch" '+%Y-%m-%dT%H:%M:%SZ')
```

Subtracting epoch seconds preserves an exact 24-hour duration across daylight-saving transitions. `America/Toronto` controls presentation and the offsets passed to Git. Strata timestamps are ISO UTC and can be compared to the UTC bounds.

### Read-only Git verification

For each candidate path, first resolve the actual worktree:

```bash
git -C "$repo" rev-parse --show-toplevel
git -C "$repo" symbolic-ref --quiet --short HEAD || git -C "$repo" rev-parse --short HEAD
```

Inspect current-branch commits and all reachable local-ref activity in the same window:

```bash
git -C "$repo" log HEAD --since="$START_LOCAL" --until="$END_LOCAL" \
  --date=iso-strict --format='%H%x09%cI%x09%an%x09%s%n%b'
git -C "$repo" log --all --since="$START_LOCAL" --until="$END_LOCAL" \
  --date=iso-strict --format='%H%x09%cI%x09%D%x09%s'
```

For relevant commits only:

```bash
git -C "$repo" show --no-ext-diff --stat --format=fuller "$commit"
git -C "$repo" diff-tree --no-commit-id --name-status -r "$commit"
git -C "$repo" cat-file -e "$claimed_commit^{commit}"
```

Inspect worktree and locally known upstream state:

```bash
git -C "$repo" status --porcelain=v1 --untracked-files=all
upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
git -C "$repo" rev-list --left-right --count HEAD..."$upstream"
```

The left count is commits local `HEAD` has beyond the configured upstream; the right count is commits the locally cached upstream has beyond `HEAD`. Since fetching is prohibited, always label this “relative to locally cached upstream ref.” Missing upstream is a status to report, not proof of unpushed work.

Verification should compare claimed hashes, subjects, changed paths, and rough diff scope to the note. If expanded test coverage is claimed, check whether appropriate test/spec/fixture paths changed and whether the note records actual test output; changed test files alone do not prove tests passed. Default mode must not execute tests. Optional deep mode may run only explicitly configured lightweight, read-only checks and must never install dependencies or mutate generated artifacts.

### Missing-note and discrepancy detection

Scan every valid inventory path, not only note-mentioned repositories. Flag:

- commits in the window with no task-level Strata cluster;
- dirty/untracked repositories with no matching active/in-progress note;
- local branches ahead of their cached upstream;
- unusually broad changes without narrative evidence;
- activity in configured archived/experimental/low-priority repositories;
- Strata code claims with no repository, missing path, missing commit, hash mismatch, or no technical activity;
- recurring agent sessions that claim completion but omit a final handoff/verification record.

Match at task level, not hash-only. A single handoff may legitimately cover a commit series, and one cross-repository campaign may cover many mechanically similar commits. Conversely, a repository-name mention is not sufficient when the claimed outcome does not align with the commits.

## 4. Optional configuration recommendation

A configuration file is recommended because priorities, explicit non-RepoRadar repositories, exclusions, archived repositories, and output destination are not represented reliably in Strata. Do not store tokens in it.

```yaml
version: 1
report:
  timezone: America/Toronto
  window_hours: 24
  output: /Users/robertdevore/2026/reports/ecosystem-daily.md
  expensive_verification: false

strata:
  repo: /Users/robertdevore/2026/strata
  base_url: http://127.0.0.1:3939
  # Token comes only from STRATA_API_TOKEN.

reporadar:
  base_url: http://127.0.0.1:8080
  enabled: true
  use_as_inventory_only: true

repositories:
  explicit: []
  roots:
    - /Users/robertdevore/2026/Kujolang/kujo-repos
    - /Users/robertdevore/2026
  max_discovery_depth: 3
  exclusions:
    - "**/node_modules/**"
    - "**/.git/**"
    - "**/vendor/**"
    - "**/dist/**"
    - "**/build/**"
  archived: []
  experimental: []
  low_priority: []

priorities:
  current_focus: []
  categories:
    kujo-language: [kujo]
    agent-infrastructure: [agents-sdk, ai-sdk, relay, signalbox]
    reliability-verification: [watchdog, casefile, fence, lens, eval]
    workflows-skills: [kujo-workflows, kujo-skills]
    updraft-central: [updraftcentral, teamupdraft]
```

Necessary fields are report time zone/window, Strata repository/endpoint, and at least one inventory source. `current_focus`, archived/experimental/low-priority lists, and category aliases are necessary for defensible priority-drift analysis. Output and expensive verification are optional.

## 5. Example report

# Daily ecosystem activity — 2026-07-16

**Window:** 2026-07-15T18:40:25-04:00 to 2026-07-16T18:40:25-04:00 (America/Toronto), equivalent to 2026-07-15T22:40:25Z to 2026-07-16T22:40:25Z.

## Executive summary

The day concentrated on Kujo agent infrastructure and local AI reliability: AI Chat gained resilient streaming, provider-neutral search/browser execution, incremental persistence, and deeper Watchdog telemetry; Watchdog gained protected dashboards, granular traces, API-value estimates, and encrypted daily backups; SignalBox/Relay matured into a reviewable authenticated execution path. CMS authoring and a cross-repository artifact-hygiene campaign also advanced. Git evidence aligns with the principal Strata completion records, and the active repositories were clean and synchronized at review time.

## What I worked on yesterday

I mainly hardened the local Kujo AI stack: AI Chat, Watchdog, SignalBox, and Relay now have more reliable execution, richer tracing, browser/search tools, and operational backups. I also advanced the CMS editing experience and standardized tool-artifact hygiene across the Kujo repositories.

## Verified progress

- **AI Chat runtime and reliability — High confidence.** Strata clusters describe complete streaming recovery, provider-neutral tools, web search, local Playwright browser execution, granular tracing, and incremental persistence. The claimed commits, including `ce7f26e`, `4c248e6`, `c95613a`, `248643d`, `8f4acc8`, and `c468066`, exist on `main`; the repository had 31 commits in the window, was clean, and matched `origin/main` using local refs.
- **Watchdog observability and operations — High confidence.** Notes and Git agree on protected dashboard work, granular traces, direct-provider value estimates, and encrypted SQLite backups. Claimed commits `55e02f8`, `acb6b35`, and `87dbf89` exist; the repository had 15 window commits, was clean, and matched local `origin/main`.
- **SignalBox/Relay agent execution — High confidence.** Strata records the streamed, budgeted, authenticated, reviewable execution path across SignalBox, Relay, AI SDK, and Watchdog. The cited commit series exists in the relevant repositories; all were clean and synchronized to their configured local upstream refs.
- **CMS experience — High confidence.** The canonical `cms-experience` repository contains the recorded admin/public app, live integration, Studio workflows, full-page editor, media, and image-containment commits. The related CMS branch and CMS Experience main branch were clean and matched their configured upstreams.
- **Kujo artifact hygiene — High confidence, mechanical campaign.** A single Strata cluster covers the repeated ignore/guard rollout. Git found the expected repeated commit subjects across 40 repositories. This is one ecosystem safeguard, not 120 separate accomplishments.

## Planning, research, and non-code work

- Provider/tool architecture decisions established that AI Chat owns provider-neutral executors while Watchdog remains an optional passive telemetry collector. **Medium confidence** as a durable design decision, with implementation evidence raising the related shipped work to High.
- A nine-test model evaluation recorded distinct roles for three Ollama Cloud models. The report artifact and Strata evidence support the research result; model quality claims remain bounded to the recorded evaluation. **Medium confidence.**

## In progress or unfinished

- The browser runtime remains deliberately read-only for consequential actions until a real approval UI exists. This is a documented limitation, not a failed completion claim.
- Some encrypted-provider credentials may require restoring the original encryption secret or re-entering keys; code now reports the condition but cannot recover mismatched ciphertext.
- The broad artifact-hygiene rollout still had repositories without upstreams in the recorded handoff; absence of an upstream prevents push verification.

## Needs attention

- `scramble-decode` had two untracked `.relay/.../workspace/` entries and no matching Strata record in the window. **Unrecorded.** Inspect whether they are disposable workflow residue or unfinished work; do not delete automatically.
- RepoRadar returned seven tracked paths that were not current Git worktrees. Inventory maintenance would reduce false warnings.
- Upstream comparisons were based on locally cached refs because the report intentionally did not fetch. Remote freshness is therefore not proven.

## Ecosystem themes

- Agent infrastructure and reliable execution
- Local AI observability and operations
- Provider-neutral tools and secure browser/search execution
- CMS authoring experience
- Cross-repository workflow hygiene

## Repository status

| Repository | Window activity | Status | Confidence/attention |
| --- | ---: | --- | --- |
| `ai-chat` | 31 commits | clean; aligned to cached `origin/main` | High |
| `watchdog` | 15 commits | clean; aligned to cached `origin/main` | High |
| `signalbox` | 21 commits | clean; aligned to cached `origin/main` | High |
| `relay` | 10 commits | clean; aligned to cached `origin/main` | High |
| `cms-experience` | 7 commits | clean; aligned to cached `origin/main` | High |
| `scramble-decode` | no window commits | two untracked Relay workspace paths | Unrecorded; attention |

## Strata coverage gaps

- No strong task-level coverage gap was found for the major commit clusters. A few intermediate hashes were not written verbatim into Strata, but their task-level handoffs and final evidence covered the series.
- The `scramble-decode` dirty state had no corresponding Strata note.
- Two non-project notes in the window were personal/tool content and were excluded from ecosystem accomplishments.

## Recommended focus today

1. Resolve or intentionally document the untracked Relay workspaces in `scramble-decode`.
2. Add a point-of-risk approval flow before widening AI Chat browser actions.
3. Prune or repair stale RepoRadar inventory entries and record current focus categories for stronger drift detection.

## 6. Gaps and recommendations

### Required blockers

There is no blocker to running the automation today: complete reads are possible through `GET /notes`, RepoRadar supplies a useful inventory, and Git supplies verification. High-assurance unattended operation does have two implementation gaps: Strata lacks server-side time filters/pagination, and priority drift has no canonical current-focus source. The proposed complete API read and small configuration file are required workarounds.

### Useful improvements

- Add `created-after`, `created-before`, `updated-after`, `updated-before`, exact ISO timestamp/time-zone validation, cursor pagination, total count, and JSONL output to Strata CLI/API.
- Fix the Commander registration for `agent context search` and add a test proving the supplied phrase, rather than the literal token `search`, reaches `searchNotes`.
- Add structured optional note metadata for repository paths/slugs, task/session/chat/run IDs, note type/status, source artifacts, commits, branch, validation, push state, and supersession relationships.
- Add a read-only `strata report activity --since ... --until ... --json` command that returns complete candidates without consolidating or mutating notes.
- Standardize agent completion records on the session template and explicitly distinguish code, non-code, plan, failed attempt, partial, and completed outcomes.
- Add RepoRadar `health` and `list --json --include-archived` commands that do not scan, write exports, or update snapshots.
- Make RepoRadar identify invalid paths and stale snapshots separately, and provide a stable machine-readable inventory endpoint/version.
- Maintain current priorities, archived/experimental classifications, and category aliases in a small automation config or another canonical local source.

### Optional enhancements

- Add task-level content fingerprints and explicit `part-of` cluster IDs to Strata memories.
- Store lightweight validation receipts as linked artifacts rather than prose-only claims.
- Add report trend metrics for repeated missing handoffs, unresolved dirty worktrees, and recurring unpushed branches without equating volume with productivity.
- Add an opt-in deep mode for configured lightweight checks, with per-repository time budgets and strict no-install/no-write enforcement.

## 7. Complete daily automation mega prompt

Copy the complete section below into the recurring Codex automation.

---

# MEGA PROMPT — Daily Ecosystem Activity Report

You are generating a read-only daily report answering “what changed across the ecosystem?” Use Strata as the primary narrative source, a repository inventory for coverage, and local Git as technical verification. Produce a concise human digest, not a note dump or commit log.

## Configuration

Use these defaults unless the automation supplies overrides:

```text
STRATA_REPO=/Users/robertdevore/2026/strata
STRATA_API_BASE_URL=http://127.0.0.1:3939
REPORADAR_API_BASE_URL=http://127.0.0.1:8080
REPORT_TIME_ZONE=America/Toronto
WINDOW_HOURS=24
REPOSITORY_ROOTS=/Users/robertdevore/2026/Kujolang/kujo-repos,/Users/robertdevore/2026
EXPLICIT_REPOSITORIES=
EXCLUDED_PATHS=node_modules,.git,vendor,dist,build
ARCHIVED_REPOSITORIES=
EXPERIMENTAL_REPOSITORIES=
LOW_PRIORITY_REPOSITORIES=
CURRENT_FOCUS_AREAS=
EXPENSIVE_VERIFICATION=false
OUTPUT_DESTINATION=
```

Read `STRATA_API_TOKEN` only from the environment. Never print, log, persist, or interpolate its value into a report. If a maintained YAML config exists, it may override the non-secret values above. Do not invent priorities when `CURRENT_FOCUS_AREAS` is empty; state that priority-drift assessment is limited.

## Absolute safety contract

Operate read-only. Do not modify Strata data or access Strata's SQLite file directly. Do not create, update, consolidate, archive, star, unstar, revert, or delete notes. Do not invoke Strata agent capture/decision/todo/summary commands.

Do not modify any repository or RepoRadar registry. Do not pull, fetch, clone, checkout, switch branches, reset, clean, stash, commit, push, merge, rebase, install dependencies, run formatters, regenerate files, or execute destructive commands. Do not invoke RepoRadar `scan`, `scan-all`, `add`, `remove`, `discover`, `export`, import, bulk scan, or any non-GET API.

Do not run test suites in default mode. `EXPENSIVE_VERIFICATION=true` permits only explicitly configured lightweight read-only checks that are already installed, have a time budget, and are known not to write files. Otherwise inspect recorded validation evidence and committed test changes only.

Never expose secrets, private note bodies, full raw diffs, credential paths unless essential and non-sensitive, or personal notes unrelated to ecosystem work. Use temporary files with restrictive defaults and remove them when finished. Do not fabricate intent, completion, priority, or verification.

## Step 1 — Calculate one exact reporting window

Set the end instant once. Use a rolling `WINDOW_HOURS` interval in epoch seconds, then render both local and UTC timestamps:

```bash
WORK_TMP=$(mktemp -d)
trap 'rm -rf "$WORK_TMP"' EXIT
end_epoch=$(date +%s)
start_epoch=$((end_epoch - WINDOW_HOURS * 3600))
START_LOCAL=$(TZ="$REPORT_TIME_ZONE" date -r "$start_epoch" '+%Y-%m-%dT%H:%M:%S%z')
END_LOCAL=$(TZ="$REPORT_TIME_ZONE" date -r "$end_epoch" '+%Y-%m-%dT%H:%M:%S%z')
START_UTC=$(date -u -r "$start_epoch" '+%Y-%m-%dT%H:%M:%SZ')
END_UTC=$(date -u -r "$end_epoch" '+%Y-%m-%dT%H:%M:%SZ')
```

Use these unchanged bounds for every Strata and Git query. Print both local bounds with `America/Toronto` and UTC bounds at the top of the report. The interval is inclusive at both ends for reporting purposes. If running on a non-BSD platform, use an equivalent epoch-to-ISO conversion while preserving the exact instants.

## Step 2 — Check Strata safely

Run from the Strata repository:

```bash
cd "$STRATA_REPO"
npm run strata -- --agent --json health
npm run strata -- --agent --json config show
```

Optionally run `config doctor --json` for diagnostics. Treat exit code 3 as unavailable, 4 as authentication failure, and 8 as timeout. If unavailable, record the limitation and continue to repository inventory/Git; do not make narrative claims that require Strata.

Do not use `notes list --limit 500` as the complete source. Strata 0.6.0 truncates that CLI path to 500 notes, has no pagination, and this installation contains more than 500 notes.

## Step 3 — Retrieve and window-filter all Strata notes

Use authenticated `GET /notes`, which returns all non-deleted notes ordered by `updatedAt`. Use Node's built-in fetch so the token remains in the environment:

```bash
node --input-type=module - "$STRATA_API_BASE_URL" "$WORK_TMP/strata-all.json" <<'NODE'
import fs from 'node:fs'
const [baseUrl, output] = process.argv.slice(2)
const headers = {}
if (process.env.STRATA_API_TOKEN) headers.Authorization = `Bearer ${process.env.STRATA_API_TOKEN}`
const response = await fetch(`${baseUrl.replace(/\/$/, '')}/notes`, { headers })
if (!response.ok) throw new Error(`Strata GET /notes failed: HTTP ${response.status}`)
const payload = await response.json()
if (!payload || !Array.isArray(payload.notes)) throw new Error('Unexpected Strata /notes response')
fs.writeFileSync(output, JSON.stringify(payload))
NODE
```

Filter locally using both timestamps:

```bash
jq --arg start "$START_UTC" --arg end "$END_UTC" '
  [.notes[] |
   select((.createdAt >= $start and .createdAt <= $end) or
          (.updatedAt >= $start and .updatedAt <= $end))]
' "$WORK_TMP/strata-all.json" > "$WORK_TMP/strata-window.json"
```

Preserve for each candidate whether it matched creation, update, or both. An older note updated during the window is an in-window record change, not proof that its original work happened during the window. Exclude personal/unrelated notes unless they have clear ecosystem project/repository/task evidence. Archived or superseded notes may explain an in-window correction but must not be presented as current.

Strata fields are only `id`, Markdown `content`, `createdAt`, `updatedAt`, `starred`, `archived`, `tags`, `projectId`, and `deletedAt`. Repository, task, session, note type, status, source, validation, and consolidation are conventions inside content/tags, not first-class filters. Parse them defensively.

Use `npm run strata -- --agent --json notes get <UUID>` only if a selected record must be re-read. Use `GET /notes/<UUID>/backlinks` or `/related` only for a specific high-value cluster; do not expand the entire graph.

## Step 4 — Extract claims without overexposing notes

For each relevant note, extract only:

- note ID, title, created/updated timestamps, project ID/name, tags;
- explicit note type/status/authority/confidence/supersession state;
- task/goal and reason/intent;
- work performed and claimed outcome;
- absolute repository path(s), slugs, project/category, branch;
- commit hashes, changed-file references, source artifacts;
- tests/validation and commit/push/cleanliness claims;
- task/issue/PR/session/chat/run/RunLedger identifiers;
- remaining limitations, failures, blockers, commitments, and next steps.

Do not reproduce full bodies in the report. Redact secrets, personal content, tokens, raw environment values, and unnecessary private paths.

## Step 5 — Deduplicate and consolidate records

Classify each note as session/handoff, state snapshot, decision, correction, constraint, procedure, lesson, TODO/commitment, plan/research, implementation capture, failed attempt, or unrelated.

Cluster using this evidence order:

1. same explicit memory/session/chat/run/task/issue ID;
2. explicit relationships such as `derived-from`, `learned-from`, `part-of`, or `supersedes`;
3. overlapping claimed commit hashes;
4. same absolute repository set plus materially identical goal/outcome;
5. same repo tags, distinctive artifact paths, title, and close timestamps.

Within a cluster, prefer the newest non-superseded state snapshot or final handoff as the anchor. Treat atomic decisions, lessons, corrections, and terse captures as supporting facets. Do not count them as separate accomplishments unless they have a distinct outcome/evidence set.

Split large notes only where they contain genuinely distinct outcomes, repositories, or code versus non-code work. Keep plans, research, failed attempts, and incomplete work out of “Verified progress.” Merge repeated mechanical campaigns by shared subjects/timestamps/file patterns. Do not equate note count, commit count, or diff size with productivity.

When multiple agents duplicate or contradict a claim, choose the strongest scoped evidence, retain the contradiction in `Needs attention`, and lower confidence. Never silently accept an active note contradicted by a newer correction or superseding record.

## Step 6 — Build repository inventory

Use this preference order:

1. absolute repository paths explicitly recorded in the selected Strata clusters;
2. a canonical Strata inventory, if a future version exposes one (Strata 0.6.0 does not);
3. RepoRadar read-only inventory;
4. configured explicit repositories and roots;
5. bounded filesystem discovery as a final fallback.

For RepoRadar, request only:

```bash
curl -fsS "$REPORADAR_API_BASE_URL/api/repos" > "$WORK_TMP/reporadar-repos.json"
```

The response has `{success, count, repos}` and includes non-archived tracked paths plus possibly stale status snapshots. Use only `repos[].path`, `group_name`, `tags`, and archive/priority metadata as inventory hints. Do not trust its cached cleanliness, branch, ahead/behind, or latest-commit fields as current verification. Validate every path with Git. If RepoRadar is unavailable, report that and continue with configured sources.

Filesystem fallback must be bounded to configured roots/depth, skip excluded directories, and only identify directories where `git -C <path> rev-parse --show-toplevel` succeeds. Do not traverse the whole home directory.

Deduplicate paths by `git rev-parse --show-toplevel`. Preserve aliases so slug-only Strata claims can map to a canonical path. Include configured archived/experimental/low-priority repositories in the omission scan when available, but label them.

## Step 7 — Verify Strata code claims with Git

For every note-mentioned repository and every inventory repository with activity/status concerns, run read-only Git commands:

```bash
git -C "$repo" rev-parse --show-toplevel
git -C "$repo" symbolic-ref --quiet --short HEAD || git -C "$repo" rev-parse --short HEAD
git -C "$repo" log HEAD --since="$START_LOCAL" --until="$END_LOCAL" \
  --date=iso-strict --format='%H%x09%cI%x09%an%x09%s%n%b'
git -C "$repo" log --all --since="$START_LOCAL" --until="$END_LOCAL" \
  --date=iso-strict --format='%H%x09%cI%x09%D%x09%s'
git -C "$repo" status --porcelain=v1 --untracked-files=all
```

For each claimed or material commit:

```bash
git -C "$repo" cat-file -e "$commit^{commit}"
git -C "$repo" show --no-ext-diff --stat --format=fuller "$commit"
git -C "$repo" diff-tree --no-commit-id --name-status -r "$commit"
```

For configured-upstream state:

```bash
upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
if [ -n "$upstream" ]; then
  git -C "$repo" rev-list --left-right --count HEAD..."$upstream"
fi
```

Interpret the left count as local-ahead and the right count as local-behind relative only to the locally cached upstream ref. Never claim remote freshness because fetching is forbidden. A missing upstream is “upstream not configured,” not automatically “unpushed.”

Compare note claims with repository existence, branch, hashes, subjects/bodies, changed paths, diff statistics, cleanliness, untracked paths, and cached upstream divergence. A claimed hash may be outside the window but still valid supporting evidence; state that distinction. If test coverage is claimed, check for related test/spec/fixture changes and recorded validation evidence, but do not infer that tests passed merely because files changed.

## Step 8 — Detect repository work missing from Strata

Across the full valid inventory, identify:

- commits in the exact window without a matching task-level Strata cluster;
- dirty worktrees or untracked files without a matching active/in-progress note;
- branches ahead of cached upstream refs;
- unusual broad changes without a narrative record;
- activity in archived, experimental, low-priority, or off-focus repositories;
- Strata-mentioned repositories with no corresponding technical activity;
- claimed commits that do not exist or do not align with the claimed work;
- repeated agent/workflow patterns that omit a final completion/handoff record.

Match omissions at task level, not only by exact hash. A final handoff may cover an intermediate series, and a cross-repository mechanical campaign may cover many equivalent commits. Conversely, a generic repository mention does not cover unrelated work.

Generated files, dependency churn, formatting-only changes, local workflow artifacts, metadata updates, and repeated guard commits are not major accomplishments without context. Report them only when they represent a meaningful safeguard, risk, or coverage gap.

## Step 9 — Analyze priorities and confidence

Compare activity themes/repositories with configured `CURRENT_FOCUS_AREAS`, archived/experimental/low-priority lists, and explicit project metadata. Flag unexpected work, scope expansion, or concentration away from priorities only when a canonical/configured priority supports the judgment. If priorities are absent, say `Priority drift: not assessable from configured evidence`.

Assign exactly one confidence class to each material item:

- **High confidence:** Strata narrative matches repository/path/commit/status evidence.
- **Medium confidence:** Strata is detailed and internally consistent, but Git verification is unavailable, not applicable, or limited to non-code evidence.
- **Low confidence:** completion is claimed but support is missing, incomplete, outside the relevant window without explanation, or contradictory.
- **Unrecorded:** repository activity/status concern exists without a matching Strata record.

Do not state that work was completed when evidence shows only a plan, attempt, partial result, failed validation, or claim.

## Step 10 — Write the report

Keep the report concise and use exactly these sections:

```markdown
# Daily ecosystem activity — YYYY-MM-DD

**Window:** START_LOCAL to END_LOCAL (America/Toronto), equivalent to START_UTC to END_UTC.

## Executive summary
One concise paragraph covering the most meaningful progress and principal risk.

## What I worked on yesterday
One to three conversational sentences that can be repeated to a colleague.

## Verified progress
Consolidated accomplishments with repositories/evidence and confidence.

## Planning, research, and non-code work
Specifications, architecture, prompts, decisions, analysis, and other meaningful non-Git work.

## In progress or unfinished
Started but incomplete, uncommitted, unpushed, unvalidated, blocked, or not cleanly concluded.

## Needs attention
Dirty/untracked repos, cached-unpushed commits, failed validation, contradictions, missing evidence/notes, unexpected work, and scope drift.

## Ecosystem themes
Only a few themes supported by actual activity.

## Repository status
Only changed, dirty, divergent, missing, contradictory, or otherwise noteworthy repositories.

## Strata coverage gaps
Repository activity without notes and Strata claims without support.

## Recommended focus today
No more than three practical recommendations.
```

Do not include every unchanged repository, every commit, raw note bodies, long diffs, or secret/private content. Include enough hashes/paths to make high-value verification auditable without turning the report into a ledger.

## Failure handling

- If Strata is unavailable: state the exact category (unavailable/auth/timeout), produce a Git/inventory-only report, mark narrative confidence accordingly, and do not imply notes were checked.
- If RepoRadar is unavailable: use note paths plus configured inventory/fallback discovery and state reduced omission coverage.
- If a repository is missing/not Git/unreadable: list it once with the limitation and continue.
- If a Git command fails: preserve the command category and sanitized error, lower confidence, and continue other repositories.
- If upstream is absent: report `no configured upstream`; do not call it pushed or unpushed.
- If locally cached refs may be stale: state that remote freshness was not checked because fetch is prohibited.
- If no Strata or Git activity exists: produce a short zero-activity report plus any dirty/divergent concerns.
- If evidence conflicts: report the contradiction; never choose a completion story without support.

## Completion criteria

The automation is complete only when it has:

1. printed one exact local/UTC window and reused it everywhere;
2. checked Strata health and either retrieved the complete `/notes` set or reported failure honestly;
3. selected both created-in-window and updated-in-window records;
4. consolidated duplicates and separated completed, non-code, failed, and unfinished work;
5. built the best available repository inventory and validated paths;
6. performed read-only Git verification for note claims and inventory activity;
7. checked for both missing Git evidence and missing Strata records;
8. classified uncertainty with High/Medium/Low/Unrecorded;
9. assessed priority drift only from configured evidence;
10. emitted the concise report structure above with at most three recommendations;
11. made no mutation to Strata, RepoRadar, repositories, branches, dependencies, or remotes.

End after writing the report. Do not create a Strata summary note, commit the report, push changes, or perform cleanup inside repositories.
