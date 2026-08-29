# Owned Agent Project

This executable kit proves the repository-owned Kujo Agent Project lifecycle:
scaffold, pinned dependency installation through Kennel, contract diagnosis,
inspection, deterministic Agents SDK execution, and Eval delegation.

## Run

Requirements: a built Kujo binary containing `kujo agent`, `kennel` on `PATH`,
Git, and network access for the initial pinned Kennel install.

```bash
export KUJO_BIN=/absolute/path/to/kujo
(cd owned-agent-project && bash scripts/run.sh)
```

Set `OUT_ROOT` to choose the evidence directory. The script refuses to reuse an
existing project directory. It writes command JSON plus `SUMMARY.md` under a
timestamped run directory. Provider credentials are not needed because the
generated project uses deterministic fixture mode.

This workflow validates the supported local development contract. It does not
claim hosted execution, provider availability, or sandboxing. Kujo capabilities
authorize effects; use the hardened profile and Workcell for a container-backed
boundary.
