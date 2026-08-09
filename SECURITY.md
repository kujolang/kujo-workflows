# Security Policy

## Supported Version

Security fixes are applied to the current `0.1.x` technical-preview line. Older snapshots and unmerged branches are not supported release baselines.

## Reporting a Vulnerability

Use GitHub's private **Report a vulnerability** flow when it is available for this repository. If private reporting is unavailable, contact a repository maintainer through the Kujolang organization without including exploit details, credentials, customer data, or sensitive evidence in a public issue.

Include the affected workflow or contract, impact, reproduction conditions, host/runtime details, and the smallest safely redacted evidence bundle. Allow maintainers time to confirm the report before public disclosure.

## Scope

These workflow kits can invoke local commands, browsers, containers, sibling Kujo tools, and opt-in external providers. Review every workflow's prerequisites and approval boundaries before running it. Fixture modes do not establish the security of a live deployment.

This repository does not provide a hosted runner, universal sandbox, secrets manager, authenticated multi-tenant service, or compliance certification. Security issues in an underlying Kujo tool should also be reported to that tool's repository.
