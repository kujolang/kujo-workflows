# VideoOps Media Generation

Runs the bounded Media Generator fixture contract. It processes only manifest records explicitly marked `GENERATE`, creates one deterministic local SVG proof asset, skips every other record, updates provenance, and records that no live provider was exercised.

```bash
bin/run --fixture --workspace /absolute/project/path --run-id example
```

The fixture proves routing, scope, file, and manifest contracts. It does not claim live image/video-provider quality.

## Shared production media execution

```bash
bin/run --media --operation import --workspace /absolute/project \
  --request /absolute/project/requests/local-media.json \
  --runtime-root /absolute/kujo-agents/videoops/tools
```

By default the bridge discovers the sibling `kujo-agents/videoops/tools` package.
Use `--agents-root /absolute/kujo-agents` for another agent checkout, or
`--runtime-root /absolute/kujo-agents/videoops/tools` for an explicit tools root.
The retired standalone repository is not required.

Use `--operation generate` for explicitly authorized GENERATE requirements.
The strict request, persistent authority, contained paths, metadata validation,
result, manifest and handoff are owned by the shared kujo-agents/videoops/tools runtime. This
wrapper invokes that CLI directly; it does not implement a provider or mixer.
`--fixture` and `--media` are mutually exclusive. Local import performs no network
access. Generation needs separately scoped provider authorization; mere credential
presence is insufficient. No operation grants publication authority.

Speech/SFX/music capabilities, account entitlement and verification status are
independent. The runtime implements ElevenLabs adapters and local import; inspect
its doctor/providers output and documentation for current tested capabilities.
The remaining creative stages stay harness-owned. A media result is acquisition
evidence, not rights approval or an autonomous film. HyperFrames consumes approved
local assets; actual independent audiovisual approval remains required.
