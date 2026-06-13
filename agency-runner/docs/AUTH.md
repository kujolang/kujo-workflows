# Auth

Logged-in workflows are first-class.

Supported strategy names:

- `no-auth`
- `saved-browser-session`
- `username-password`
- `cookie-injection`
- `custom-command`

The prototype implements saved browser session generation for username/password profiles:

```bash
export ACME_CUSTOMER_USERNAME="test@example.com"
export ACME_CUSTOMER_PASSWORD="..."
agency-loop login --site acme --role customer
```

Manual fallback:

```bash
agency-loop login --site acme --role customer --manual
```

The command writes:

```text
.kujo/agency/auth/<site>/<role>.storage-state.json
.kujo/agency/auth/<site>/<role>.health.json
.kujo/agency/auth/<site>/<role>.login.log
```

Passwords are read from environment variables and are not written to handoff artifacts. Redaction rules are applied to login logs after the helper exits.
