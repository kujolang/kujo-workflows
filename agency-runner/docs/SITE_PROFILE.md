# Site Profile

Site profiles live at:

```text
.kujo/agency/sites/<site>.yml
```

A profile defines:

- CMS or app type.
- Environment and base URL.
- Repo path.
- Auth roles and saved-session paths.
- Safety gates.
- Source roots and excluded paths.
- Reset hooks.
- Recipes enabled for the site.
- Redaction rules.

Create one with:

```bash
agency-loop site add acme --type wordpress --environment staging --base-url https://staging.example --repo-path "$PWD"
```

Validate by inspection against:

```text
schemas/site-profile.schema.json
```

Production profiles are blocked by default unless `safety.allow_production: true`.
