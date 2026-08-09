.PHONY: validate lint format test

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
