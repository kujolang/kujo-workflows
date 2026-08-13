.PHONY: validate lint format test release clean-checkout

validate: lint test

lint:
	python3 scripts/validate_docs.py
	python3 scripts/validate_static.py
	python3 scripts/validate_catalog.py --structure-only --json
	python3 scripts/validate_contracts.py

format:
	git diff --check

test:
	python3 -m unittest discover -s tests -p 'test_*.py'
	bash tests/test_codebase_cleanup.sh

release:
	bash tests/release-readiness.sh

clean-checkout:
	bash tests/clean-checkout.sh
