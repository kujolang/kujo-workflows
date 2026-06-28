# DocsGen Repo Contract Runner HOWTO

## 1. Run The Demo

```bash
cd docsgen-repo-contract-runner
bash scripts/run-workflow.sh
```

The demo creates a small fixture repo inside `.runs/<timestamp>/fixture/` and runs DocsGen against it.

## 2. Run Against A User-Chosen Repo

```bash
TARGET_REPO=/path/to/repo bash scripts/run-workflow.sh
```

Useful overrides:

```bash
TARGET_REPO=/path/to/repo \
DOCGEN_LANGUAGES=typescript,javascript,python \
DOCGEN_FORMAT=all \
DOCGEN_PUBLIC_ONLY=1 \
bash scripts/run-workflow.sh
```

Strict gate mode:

```bash
TARGET_REPO=/path/to/repo DOCGEN_STRICT=1 bash scripts/run-workflow.sh
```

Strict mode enables:

- `--public-only`
- `--fail-on-undocumented`
- `--fail-on-broken-links`
- `--fail-on-warnings`

## 3. Review The Output

Open:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/artifacts/agent-handoff.md
.runs/<timestamp>/logs/docgen-command.txt
.runs/<timestamp>/logs/docgen-cli.json
.runs/<timestamp>/logs/docgen.stderr
.runs/<timestamp>/generated-docs/
```

Important generated files usually include:

```text
generated-docs/index.html
generated-docs/docgen.md
generated-docs/docgen.json
generated-docs/docgen-gaps.json
generated-docs/docgen-capabilities.json
generated-docs/docgen-ai-tasks.md
generated-docs/search-index.json
generated-docs/symbol-index.json
```

## 4. Agent Usage Pattern

When using this workflow with the DocsGen skill:

1. Ask the user for the target repo path or infer it from the active task.
2. Run `TARGET_REPO=/path/to/repo bash scripts/run-workflow.sh`.
3. Inspect `SUMMARY.md`, `logs/docgen-cli.json`, and `generated-docs/docgen-gaps.json`.
4. If the task is a public docs refresh, compare generated output to README/reference claims before writing committed docs.
5. Use `DOCGEN_STRICT=1` only when the user wants a gate, not just discovery.

## 5. Troubleshooting

If DocsGen exits nonzero, the workflow still writes a summary and logs before returning the same exit code. Inspect:

```text
logs/docgen.stderr
logs/docgen-cli.json
status.tsv
```

For very large repos, set discovery limits:

```bash
TARGET_REPO=/path/to/repo \
DOCGEN_MAX_FILES=2000 \
DOCGEN_MAX_DEPTH=8 \
bash scripts/run-workflow.sh
```

The script maps those values to `--max-discovery-files` and `--max-discovery-depth`.
