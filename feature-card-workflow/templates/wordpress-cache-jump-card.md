# CARD-123 Cache jump fix

## Problem

After cached markup loads, the page jumps unexpectedly on pages using the plugin widget.

## Desired Behavior

The cached widget initializes without causing a visible page jump. Existing PHP cache behavior remains compatible.

## Scope

In scope:

- JavaScript initialization, event timing, scroll/layout behavior, and duplicate handler prevention.
- PHP cache key, invalidation, transient/object-cache, or rendered markup tweaks directly tied to the jump.
- Focused tests or fixtures that prove the cache behavior still works.
- Lens proof on a local WordPress page that reproduces the behavior.

Out of scope:

- Broad plugin refactors.
- Dependency upgrades unless required by the fix.
- Unrelated style or admin UI changes.

## Acceptance Criteria

- Page position remains stable after cached markup loads.
- JavaScript initialization runs once and does not trigger duplicate layout updates.
- PHP cache keys and invalidation remain backward-compatible for existing users.
- Existing PHP and JS checks pass.
- Lens records a walkthrough showing the page remains stable on the affected route.

## Technical Notes

- Local WordPress URL:
- Affected shortcode/block/widget:
- Suspected JS file:
- Suspected PHP cache file:
- Cache layer: transient/object-cache/custom/static asset cache/unknown

## Verification Expectations

- Run PHP and JS checks available in the plugin.
- Run Lens against the local page that reproduces the jump.
- Include pre-fix Lens evidence when a reproduction flow already exists.

Browser/Lens proof required:

- Yes

## Risks

- Risk: cache changes could invalidate too aggressively.
  Mitigation: keep PHP changes scoped and verify existing cache behavior.

- Risk: JS changes could hide the symptom while leaving duplicate initialization.
  Mitigation: test repeated initialization and review console/network output.

## Open Questions

- Which exact route/page reproduces the jump?
- Does the jump happen only for logged-in users, anonymous users, or both?
- Is the cache server-side, browser-side, CDN-side, or plugin-local?
