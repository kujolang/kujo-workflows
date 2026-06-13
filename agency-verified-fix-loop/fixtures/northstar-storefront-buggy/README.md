# Northstar Storefront Demo

Small PHP/JS/CSS storefront fixture for the Agency Verified Fix Loop.

## Quick Start

Install requirements:

- PHP 8+
- Node.js 18+

Run the local cart page:

```bash
php -S 127.0.0.1:8099 -t public
```

Open:

```text
http://127.0.0.1:8099/cart.php
```

## Usage

Run tests:

```bash
php tests/promo_code_test.php
```

Run JavaScript syntax check:

```bash
node --check public/assets/js/cart.js
```

## Example

The cart page has a promo-code drawer. The demo bug is that the first tap on
`Apply` arms the handler instead of applying the code. The fix changes the
behavior to form submission handling and adjusts mobile spacing around the
sticky checkout bar.
