# Publishing House workflows

The Publishing House workflow layer is an eleven-kit, local-first technical
preview for moving an editorial signal through publication evidence and back
into a follow-up recommendation. Each kit is independently runnable, and the
repository fixture composes them in this order:

```text
Governance -> Daily Desk -> Commissioning -> Evidence Dossier -> Primary Piece
                                      Primary Piece -> Asset Production
Primary Piece + Asset Production -> Editorial Review
Editorial Review -> Adaptation -> Format Production
Format Production -> Approval and Publication -> Post-Publication Learning
Post-Publication Learning -> future StoryDesk input
```

Daily Desk chooses the narrowest applicable child workflow. It can route under
`PROPOSE`, but it cannot create commissions, evidence decisions, review
verdicts, approvals, or publication receipts. Follow-up recommendations begin
a new operator-authorized run; the workflow never recurses automatically.

## Record ownership and boundaries

The workflow state contains stable references, versions, paths, and checksums.
It does not replace the owning records: StoryDesk owns editorial state;
Dossier owns evidence; GalleyPack owns versioned artifacts; BluePencil owns
reviews; AssetWorks owns media manifests; VersionSeal owns approval records;
PressWire alone creates publication effects and receipts; ReaderSignal owns
measurements and learning. Dispatch owns canonical run state, trace, report,
mutation history, and run-catalog artifacts. Agents SDK owns bounded role
execution receipts.

`OBSERVE`, `PROPOSE`, and `ACT` are upper bounds. Only the Publishing Operations
Director step in Approval and Publication may use `ACT`. Credentials do not
grant authority. A VersionSeal approval binds the exact GalleyPack checksum,
destination, action, conditions, and expiry; changing any reviewed bytes
requires a new package and approval. Dispatch's pause state is orchestration
evidence, not approval. BluePencil verdicts are editorial records, not human
publication authority.

## Install and run today

The supported installation path creates an isolated bundle containing the
eleven workflow kits, clean checkouts of every locked Kujo dependency, and the
operator-supplied Kujo binary. It refuses to overwrite an existing target and
does not require Python, model credentials, or a network when `--source-repos`
points to local checkouts:

```bash
bash scripts/install-publishing-house.sh \
  --prefix "$PWD/.local/publishing-house" \
  --source-repos /path/to/kujo-repos \
  --kujo-bin /path/to/kujo \
  --demo

.local/publishing-house/bin/publishing-house-doctor
```

Without `--source-repos`, missing dependency checkouts are cloned from the
HTTPS repositories recorded in
[`install-lock.json`](install-lock.json). The `--demo` gate runs all eleven
workflows after the staged installation is moved to its final path, so every
persisted record reference remains resolvable. The resulting
`first-run/integration-proof.json` is the installation acceptance receipt.

## Run the complete fixture from a source checkout

Provide sibling Kujo repositories under the same parent directory or set
`KUJO_REPOS` and `KUJO_BIN`, then run:

```bash
bash scripts/run-publishing-house-fixture.sh --out /tmp/publishing-house-proof
```

The fixture uses a fictional house, deterministic IDs and timestamps, fixture
agents, captured local evidence, a bounded revision, an explicitly labeled
fixture approval, and PressWire's bounded local fixture adapter. It requires no
credentials or network and cannot publish externally. The reviewed proof is in
[`../evidence/PUBLISHING_HOUSE_FIXTURE_PROOF_2026-08-14.md`](../evidence/PUBLISHING_HOUSE_FIXTURE_PROOF_2026-08-14.md).

Run one kit with its checked-in request:

```bash
(cd publishing-house-daily-desk && bash bin/run --request fixtures/request.fixture.json --json)
```

Each kit's `HOWTO.md` documents its request, test command, state files, outputs,
failure behavior, and resume boundary. The request may point to operator-owned
House, Brand, and Audience Profiles. Daily Desk also accepts a normalized
packet or the optional content-calendar adapter shape; that adapter is not a
runtime dependency.

## Fixture and live modes

Fixture mode is offline, deterministic, repeatable, credential-free, and
external-effect-free. It runs the current tool CLIs, Dispatch workflow, and
Agents SDK no-network fixture boundary. Every agent step loads the canonical
Publishing House shared contracts, role contract, role skill, and workflow
skill into the runner and records their exact paths and instruction checksum.
Capability preflight verifies that each tool, `kujo-agents`, and `kujo-skills`
checkout is clean and matches the exact tested commit; drift fails closed
before tool mutation.
Generated run directories are ignored unless deliberately promoted as reviewed
evidence.

Live mode must be selected explicitly. It performs capability and permission
preflight, requires configured compatible adapters, rejects secret-shaped
persisted input, and fails closed rather than falling back to fixture data.
Live provider and destination adapters remain operator-specific and are not
claimed by this technical preview.

## Inspection and recovery

The selected run directory contains `state.json`, `report.json`, capability and
agent receipts, tool record references, and the Dispatch state/trace/report
artifacts. Approval and Publication first exits in `paused` state with an
approval-pause record. Resume with the exact run ID and VersionSeal result:

```bash
(cd publishing-house-approval-publication && \
  bash bin/run --request fixtures/request.fixture.json --resume \
  --fixture-approval ../fixtures/publishing-house/fixture-approval.fixture.json --json)
```

Before publication, inspect the frozen GalleyPack identity and checksum,
BluePencil reviews and unresolved queries, Dossier and AssetWorks references,
VersionSeal scope, destination/action, and PressWire preflight. Repeating a
completed fixture run returns its completion record without creating a second
effect. Unsupported, unavailable, blocked, rejected, skipped, failed, and
completed outcomes remain distinct.

## Compatibility and readiness

Exact tested repository commits and contract versions are recorded in
[`compatibility-matrix.json`](compatibility-matrix.json), with command outcomes
in [`validation-report.md`](validation-report.md). All eleven kits are
installable and usable today for the locked, offline local fixture contract.
They remain classified as **Limited** rather than production-ready because
their live mode deliberately fails closed until an operator provides reviewed
model/retrieval adapters, authenticated destination adapters, and a real human
VersionSeal decision. The limit is an external/live integration boundary, not
an unverified fixture or missing installation path.
