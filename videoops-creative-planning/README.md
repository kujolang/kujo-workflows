# VideoOps Creative Planning

Runs the bounded Creative Director fixture contract. It consumes a complete PackWrite-style `intake/` packet and writes the five planning artifacts, a creative Eval receipt, a stage receipt, state event, and explicit handoff. It never sources media or renders video.

```bash
bin/run --fixture --workspace /absolute/project/path --run-id example
```

Live model execution is intentionally unavailable until an approved runtime adapter resolves the provider-neutral model profile. Missing intake fails closed.
