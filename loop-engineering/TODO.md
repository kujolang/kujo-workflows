# Todo

- [x] Select content pillar: portable agent loop (Goal → Context → Agent → Evaluation → Stop).
- [x] Map the four loop pieces onto real Kujo tooling (Spec/Watchdog/RunLedger, Scout/Scent/PackWrite/Muzzle/CaseFile/MCP+RAG, Eval/ShipCheck/ChangeBucket/Lens, Agents SDK/Dispatch).
- [x] Write the portable workflow definition (`WORKFLOW.md`).
- [x] Write the machine-readable loop contract (`loop.spec.yml`).
- [x] Ship a portable reference driver with no-op default adapters (`scripts/run-workflow.sh`).
- [x] Verify all stop conditions fire: success, repeated-failure, stall, budget.
- [x] Keep the core decentralized: no Paperclip / single-host / single-provider / single-CI assumptions.
- [x] Add README and HOWTO; register in the repo catalog.
- [x] Add repo-local `.loop-engineering/` initialization with config, ledger, summary, blockers, iterations, and evidence directories.
- [x] Make demo mode explicit and require `--config`, `--checklist`, or `--demo`.
- [x] Add Markdown checklist classification and structured external blocker capture.
- [x] Add per-iteration evidence artifacts and fixed final report contract.
- [x] Add opt-in commit/push and Strata memory hook configuration.
- [ ] Optional: ship a Dispatch workflow template that runs this loop with real Agents SDK roles.
- [ ] Optional: add a Kujo-wired example that fixes a real fixture bug end-to-end (reuse the storefront fixture from `agency-verified-fix-loop`).
- [ ] Optional: add adapters for common CI providers and issue/PR trackers under `adapters/`.
- [ ] Optional: promote the five capabilities into a first-class `kujo loop` command wrapper.
