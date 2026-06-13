{
  "name": "mobile-promo-drawer-fix",
  "description": "Agency Verified Fix Loop checks for the Northstar mobile promo-code drawer fix.",
  "version": "1.0.0",
  "output_dir": "./eval_results",
  "snapshot_dir": "./snapshots",
  "stop_on_failure": false,
  "tests": [
    {
      "name": "PHP promo-code tests pass",
      "check": "command_succeeds",
      "params": {
        "command": "php tests/promo_code_test.php"
      }
    },
    {
      "name": "Cart JavaScript syntax is valid",
      "check": "command_succeeds",
      "params": {
        "command": "node --check public/assets/js/cart.js"
      }
    },
    {
      "name": "Cart page returns HTTP 200",
      "check": "http_status",
      "params": {
        "url": "http://127.0.0.1:__PORT__/cart.php",
        "expected_status": 200
      }
    },
    {
      "name": "Fixed JS uses submit handler",
      "check": "file_contains",
      "params": {
        "path": "public/assets/js/cart.js",
        "expected": "promoForm.addEventListener('submit'"
      }
    },
    {
      "name": "Fixed CSS defines checkout bar height",
      "check": "file_contains",
      "params": {
        "path": "public/assets/css/cart.css",
        "expected": "--checkout-bar-height"
      }
    },
    {
      "name": "PHP test output confirms pass",
      "check": "output_contains",
      "params": {
        "command": "php tests/promo_code_test.php",
        "expected": "promo tests passed"
      }
    }
  ]
}
