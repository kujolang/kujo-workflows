# Northstar Mobile Promo Drawer Fix

## Stable Intent

Fix the mobile cart promo-code drawer so a customer can open the drawer, enter `SAVE10`, apply the code on the first tap, and continue checkout without the sticky checkout bar crowding the form.

## Non-Goals

- Do not redesign the cart page.
- Do not change checkout payment behavior.
- Do not change promo-code business rules.
- Do not add a JavaScript framework.

## Expected Evidence

- PHP promo-code tests pass.
- JavaScript syntax check passes.
- Eval suite passes.
- Lens mobile flow passes after the fix.
- PatchBrief, ChangeBucket, ShipCheck, and RunLedger artifacts are produced.
