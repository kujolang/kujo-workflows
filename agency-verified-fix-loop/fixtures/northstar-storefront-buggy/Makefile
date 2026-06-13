.PHONY: test lint format serve

test:
	php tests/promo_code_test.php

lint:
	node --check public/assets/js/cart.js

format:
	node -e "console.log('format check placeholder')"

serve:
	php -S 127.0.0.1:8099 -t public
