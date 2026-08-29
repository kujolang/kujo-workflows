# How to adapt the Owned Agent Project workflow

Use `PROFILE=tools`, `knowledge`, `workflow`, `hardened`, `observable`, or `full`
to exercise another generated shape. Keep the fixture provider for repeatable
CI. Test a live provider separately by editing the generated
`config/model.json`, setting only the named credential environment variable,
and retaining the generated file in version control without secret values.

Review the generated `agent.project.json`, `kennel.toml`, `kennel.lock`, and
`.env.example` before adapting the project. Run `kujo doctor agent --deep` after
each dependency or policy change.
