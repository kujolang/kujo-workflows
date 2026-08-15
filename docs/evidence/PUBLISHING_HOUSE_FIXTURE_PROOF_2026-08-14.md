# Publishing House all-eleven fixture proof

Captured: 2026-08-14

The portable all-eleven fixture completed with 11 workflow completion receipts,
46 checksum-verified tool record references, 34 exact tool-contract preflights,
38 offline Agents SDK step receipts, and 11 Dispatch state/trace sets.

Verified boundaries:

- the first package received a BluePencil revise verdict and the edited artifact became a new GalleyPack version;
- Approval and Publication paused before VersionSeal approval and resumed only with explicitly labeled fixture approval data;
- approved and locally published bytes both hashed to `828b6cbe7dbff63cd2b1e50e121c743708c3dc76f232d7f72b44fac49c2cf3ec`;
- every completed workflow accepted an idempotent replay;
- every Agents SDK step loaded the canonical shared house contracts, role
  contract, role skill, and Publishing House workflow skill, with matching
  instruction checksums in the execution receipt;
- Agents SDK receipts reported `requires_network=false`, Dispatch ran in offline fixture mode, and no credentials were required;
- PressWire produced only a bounded local fixture copy; no live publication occurred.

Reproduce with:

```bash
bash scripts/run-publishing-house-fixture.sh --out "$(mktemp -d)/publishing-house-proof"
```

The machine-readable reviewed result is [publishing-house-fixture-proof.json](publishing-house-fixture-proof.json). Ordinary generated runs remain ignored.
