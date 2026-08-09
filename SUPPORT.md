# Support

Use [GitHub Issues](https://github.com/kujolang/kujo-workflows/issues) for reproducible problems with these workflow kits, including stale commands, broken fixtures, missing artifacts, contract mismatches, and validation failures.

Before opening an issue, run:

```bash
python3 -m pip install jsonschema PyYAML
bash tests/release-readiness.sh
```

Include the workflow name, repository commit, operating system, Kujo runtime and sibling-tool versions when applicable, expected behavior, actual behavior, exit status, and relevant non-sensitive output. Questions or defects about an underlying Kujo tool should go to that tool's repository unless the problem is specific to this integration.

Do not post credentials, provider responses containing private data, customer repositories, or unredacted workflow evidence in a public issue.
