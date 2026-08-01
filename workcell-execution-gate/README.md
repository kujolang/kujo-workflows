# Workcell execution gate

This workflow validates and inspects a Workcell definition, then attempts one
bounded Docker execution against a clean Git fixture. It maps the actual
result to the versioned package and completion contracts.

If the local Docker backend cannot write the declared artifact as the mapped
non-root user, the workflow emits a `blocked` receipt and stops; it never
claims success from an incomplete run.

Run: `KUJO_BIN=/path/to/kujo workcell-execution-gate/scripts/run.sh`

By default, temporary fixture repositories are created under
`../.workcell-host-tmp` so Colima/Docker can mount them from the same host
filesystem used by Workcell. Set `WORKCELL_TMP_ROOT` to override that location
when using a different Docker host.
