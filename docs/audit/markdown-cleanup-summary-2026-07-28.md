# Markdown cleanup summary — 2026-07-28

The July 2026 ecosystem Markdown cleanup reviewed repository documentation, generated run packets, temporary workspaces, evidence bundles, stale handoffs, dated reports, templates, examples, and planning files across the local Kujo checkout.

## Durable disposition

- Keep canonical product, API, security, operations, architecture, release, template, and example documentation when it still describes a supported surface.
- Remove generated `.runs/`, tool caches, temporary workspaces, disposable agent packs, duplicate handoffs, and other reproducible local evidence unless a proof artifact is intentionally promoted for long-term review.
- Remove dated planning and review documents after their durable conclusions are incorporated into current source-of-truth documentation.
- Preserve versioned release evidence and explicit historical decisions when future work depends on their provenance.
- Prefer repository-level ignore rules and CI artifact guards over recurring manual cleanup.

## Kujo Workflows outcome

- Removed obsolete workflow docs whose surviving content was already covered by canonical READMEs, HOWTOs, scripts, or machine-readable contracts.
- Kept the active workflow catalog, compatibility matrices, weekly audit summaries, launch checklist, contract documentation, and reusable templates.
- Updated catalog documentation paths to reference files that exist in the tracked repository.
- Retained generated workflow outputs as ignored local evidence by default.

## Why the bulk inventories were removed

The original triage, needs-review, disposition, and missing-candidate inventories totaled tens of thousands of lines and primarily enumerated transient paths from sibling repositories. They were useful during the cleanup operation but were not an appropriate long-term public documentation surface. Git history preserves the exact inventories; this summary preserves the policy and outcome needed for future maintenance.

## Ongoing verification

Run the repository documentation validator and artifact guard after changing documentation policy:

```bash
python3 scripts/validate_docs.py
bash .github/scripts/check-kujo-tool-artifacts.sh HEAD^ HEAD
```
