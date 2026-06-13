# WordPress Account Settings Example

This example profile models a staging WordPress account settings task.

For a dry-run in any local repo:

```bash
agency-loop init
mkdir -p .kujo/agency/sites
cp /Users/robertdevore/2026/Kujolang/kujo-repos/agency-runner/examples/wordpress-account-settings/site-profile.yml .kujo/agency/sites/acme-wp.yml
agency-loop run --site acme-wp --recipe account-settings --file /Users/robertdevore/2026/Kujolang/kujo-repos/agency-runner/examples/wordpress-account-settings/task.md --dry-run
```

Before real login/use, edit `repo_path`, URLs, selectors, and reset hooks.
