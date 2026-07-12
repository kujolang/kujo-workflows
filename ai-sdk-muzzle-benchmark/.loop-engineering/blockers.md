# External Blockers

blockers:
  - id: typed-env-default-contract
    command: "env_int/env_float/env_bool"
    evidence: "Native typed environment accessors do not provide the benchmark's missing/blank/invalid fallback semantics; the migration therefore uses small native-backed default adapters."
    status: needs-contract-first
    next_action: "Add optional/default typed environment primitives or document their fallback contract, then remove the adapters and add invalid-value compatibility tests."
