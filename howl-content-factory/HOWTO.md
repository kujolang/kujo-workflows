# Howl Content Factory HOWTO

## 1. Run The Demo

```bash
cd howl-content-factory
bash scripts/run-workflow.sh
```

## 2. Review The Output

Open:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/showcase/howl.json
.runs/<timestamp>/showcase/examples/
.runs/<timestamp>/showcase/dist/howl/index.html
.runs/<timestamp>/showcase/dist/howl/agent-handoff.md
.runs/<timestamp>/showcase/dist/howl/agent-handoff.svg
.runs/<timestamp>/showcase/dist/howl/agent-handoff.html
.runs/<timestamp>/showcase/dist/howl/social-launch-card.svg
```

## 3. Use It In A Real Repo

From a repo with Kujo examples:

```bash
export KUJO_REPOS=/path/to/kujo-repos
export KUJO="$KUJO_REPOS/kujo/target/release/kujo"
"$KUJO_REPOS/howl/bin/howl" init
"$KUJO_REPOS/howl/bin/howl" validate
"$KUJO_REPOS/howl/bin/howl" render
```

Generate a caption:

```bash
"$KUJO_REPOS/howl/bin/howl" caption agent-handoff --platform x
```

Use `variant: "social"` in a card to render Howl's branded 1200x630 social SVG layout. Optional `background_image` and `font_file` assets must stay under the manifest directory.

## 4. Content Notes

The key proof is that Howl renders only what exists in `howl.json` and the referenced example files. It does not invent claims, call an LLM, or post anywhere.

## 5. Troubleshooting

If Howl cannot find Kujo, set:

```bash
export KUJO=/path/to/kujo
```

The launcher resolves manifests relative to the current working directory, so run Howl from the project that contains `howl.json`.
