# WordPress Account Settings Example

This example profile models a staging WordPress account settings task.

For a dry-run in any local repo:

```bash
export KUJO_WORKFLOWS=/path/to/kujo-workflows
AGENCY_LOOP="$KUJO_WORKFLOWS/agency-runner/bin/agency-loop"
"$AGENCY_LOOP" init
mkdir -p .kujo/agency/sites
cp "$KUJO_WORKFLOWS/agency-runner/examples/wordpress-account-settings/site-profile.yml" .kujo/agency/sites/acme-wp.yml
"$AGENCY_LOOP" run --site acme-wp --recipe account-settings \
  --file "$KUJO_WORKFLOWS/agency-runner/examples/wordpress-account-settings/task.md" \
  --dry-run
```

Before real login/use, edit `repo_path`, URLs, selectors, and reset hooks.
