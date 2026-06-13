{
  "name": "Mobile promo-code drawer applies code",
  "url": "http://127.0.0.1:__PORT__/cart.php",
  "viewports": ["mobile"],
  "timeout_seconds": 6,
  "allow_external": false,
  "allow_destructive": false,
  "steps": [
    {
      "visit": "http://127.0.0.1:__PORT__/cart.php"
    },
    {
      "assert_text": "Have a promo code?"
    },
    {
      "click": {
        "selector": "[data-testid=promo-toggle]",
        "safe": true
      }
    },
    {
      "wait_for_selector": "[data-testid=promo-input]"
    },
    {
      "screenshot": {
        "name": "promo-drawer-open"
      }
    },
    {
      "type": {
        "selector": "[data-testid=promo-input]",
        "value": "SAVE10"
      }
    },
    {
      "click": {
        "selector": "[data-testid=promo-apply]",
        "safe": true
      }
    },
    {
      "wait_for_text": "Promo code applied"
    },
    {
      "assert_text": "Promo code applied"
    },
    {
      "assert_no_console_errors": true
    },
    {
      "assert_no_failed_requests": true
    },
    {
      "screenshot": {
        "name": "promo-applied"
      }
    }
  ]
}
