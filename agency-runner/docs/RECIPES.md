# Recipes

Recipes live in:

```text
recipes/<recipe-id>.yml
```

A recipe provides a reusable agency workflow skeleton:

- Required auth and role.
- Entry path.
- Common actions.
- Assertions.
- Likely source paths by CMS.
- Eval suggestions.
- Optional safety requirements.

Default recipes:

- `account-settings`
- `contact-form`
- `admin-editor`
- `checkout`
- `theme-layout`
- `login-registration`
- `search-filter`
- `email-notification`
- `plugin-integration`
- `performance-regression`

Profiles can enable a subset. Runs can override recipe selection with:

```bash
agency-loop run --site acme --recipe account-settings --file task.md
```
