# Known Limitations

- The prototype creates the full workflow packet, but does not yet execute a coding backend for `agent fix`.
- Generic recipes cannot know every CMS selector. Use Lens inspect and profile overrides for production use.
- Non-dry Lens reproduction/proof phases execute against live sites, but dry-runs do not prove real browser behavior.
- Eval command generation is conservative and should be customized per project.
- Schema files are included, but runtime schema validation is not yet enforced in the CLI.
- Cookie injection and custom login commands are named in the profile contract but not fully implemented.

## Next Best Iteration

1. Add runtime schema validation.
2. Add recipe/profile overrides for concrete Lens steps and selectors.
3. Add a coding backend interface for `agent fix`.
4. Execute Lens flows directly when site/session are available.
5. Run PatchBrief, ChangeBucket, ShipCheck, and RunLedger through the actual Kujo tools for non-dry runs.
6. Add `kujo agency` shim or native Kujo command integration.
