# VideoOps Media Generation

Runs the bounded Media Generator fixture contract. It processes only manifest records explicitly marked `GENERATE`, creates one deterministic local SVG proof asset, skips every other record, updates provenance, and records that no live provider was exercised.

```bash
bin/run --fixture --workspace /absolute/project/path --run-id example
```

The fixture proves routing, scope, file, and manifest contracts. It does not claim live image/video-provider quality.
