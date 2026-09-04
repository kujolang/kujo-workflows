# VideoOps HyperFrames Edit

Runs the bounded HyperFrames Editor fixture contract against the installed current CLI. It refuses unresolved assets, writes a deterministic composition, runs `hyperframes check`, renders a real 1920×1080 30fps candidate, probes it with ffprobe, applies every fix-list item in revision mode, and finalizes only after Critic PASS.

```bash
bin/run --fixture --workspace /absolute/project/path --run-id example
bin/run --fixture --workspace /absolute/project/path --run-id example --revision --attempt 2
bin/run --fixture --workspace /absolute/project/path --run-id example --finalize --attempt 3
```

This stage does not approve its own render. Cloud render and account-backed effects are outside the fixture boundary.
