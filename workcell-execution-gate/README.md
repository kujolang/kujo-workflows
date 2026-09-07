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

## Select an existing supported daemon

The gate records `doctor.json`, `docker-security-options.json` and the exact
`workcell-definition.json`. It changes only `workspace.run_as`: `rootless` when
the selected daemon explicitly advertises rootless, otherwise `host`. Workcell
retains enforcement of seccomp, AppArmor where required, network isolation,
read-only root, dropped capabilities, resources and artifact boundaries.

Choose an existing context per invocation, for example:

```bash
DOCKER_CONTEXT=colima KUJO_BIN=/path/to/kujo workcell-execution-gate/scripts/run.sh
```

This does not call `docker context use`, provision a daemon, pull an image or
disable a profile. On 2026-09-06, the available Colima daemon advertised seccomp
and AppArmor in rootful mode; Docker Desktop did not advertise AppArmor. A
rootless run is a different supported host profile and must never be reported as
proof that AppArmor ran. Selection logic has synthetic rootful/rootless tests;
actual execution evidence must identify the observed backend.
