name: "Fix mobile promo-code drawer on cart page"
goal: "Fix the mobile cart promo-code drawer so customers can reveal the input, enter a promo code, apply it on the first tap, and continue checkout without the sticky checkout bar crowding the form."
version: "0.1.0"
priority: "high"
tags:
  - agency
  - storefront
  - mobile
  - cart
  - bugfix

background: >
  Client reports that mobile customers can open the promo-code drawer, but the
  input is hidden behind the sticky checkout bar. Some users also report that
  the Apply button does nothing on the first tap.

scope: >
  Investigate and fix the promo-code drawer behavior on the cart page for mobile
  viewport sizes. Preserve the existing cart layout and visual style.

non_goals:
  - "Redesigning the cart page"
  - "Changing checkout payment behavior"
  - "Changing promo-code validation rules"
  - "Adding a JavaScript framework"

relevant_systems:
  - "public/cart.php"
  - "public/assets/js/cart.js"
  - "public/assets/css/cart.css"
  - "src/PromoCodeService.php"
  - "tests/promo_code_test.php"

likely_files:
  - "public/cart.php"
  - "public/assets/js/cart.js"
  - "public/assets/css/cart.css"
  - "tests/promo_code_test.php"

acceptance_criteria:
  - "At mobile width, tapping 'Have a promo code?' reveals the promo-code drawer."
  - "The promo-code input is visible and not covered by the sticky checkout bar."
  - "Entering SAVE10 and tapping Apply applies the code on the first tap."
  - "A success message is visible after applying a valid promo code."
  - "Existing desktop cart layout remains unchanged."
  - "No console errors occur during the promo-code flow."
  - "No PHP promo-code tests regress."

eval_requirements:
  - description: "PHP promo-code tests pass"
    check_type: "command_succeeds"
    params:
      command: "php tests/promo_code_test.php"
  - description: "Cart JavaScript syntax check passes"
    check_type: "command_succeeds"
    params:
      command: "node --check public/assets/js/cart.js"
  - description: "Cart page responds locally"
    check_type: "http_status"
    params:
      url: "http://127.0.0.1:__PORT__/cart.php"
      expected_status: 200

risks:
  - risk: "Changing sticky checkout CSS could affect checkout conversion layout."
    severity: "medium"
    mitigation: "Limit CSS changes to cart promo drawer/mobile breakpoint and verify desktop with Lens."
  - risk: "JavaScript event binding fix could duplicate promo submission."
    severity: "medium"
    mitigation: "Use deterministic form submission handling and verify one first-tap apply path."

review_expectations:
  - "Reviewer should inspect mobile CSS changes."
  - "Reviewer should confirm no promo validation logic was changed unnecessarily."
  - "Reviewer should review Lens walkthrough proof."

human_approval_points:
  - "Before production deploy"
