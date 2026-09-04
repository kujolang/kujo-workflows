# VideoOps Asset Resolution

Runs the bounded Asset Scout fixture contract. It accounts for every approved requirement as `FOUND`, `CAPTURED`, `GENERATE`, `NOT_REQUIRED`, or `BLOCKED`, preserves rights and provenance, and hands only explicit generation work forward.

```bash
bin/run --fixture --workspace /absolute/project/path --run-id example
```

The fixture performs no web research or download and never treats public accessibility as reuse permission.
