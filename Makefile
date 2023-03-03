install:
	@python -m pip install .

build:
	@python -m build

clean:
	@rm -rf build dist src/.eggs src/*.egg-info
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '.pytest_cache' -exec rm -rf {} +

format: clean
	@python -m black src/ tests/

lint:
	@python -m ruff src/ tests/

static-check:
	@python -m mypy src/ tests/

.PHONY: tests

tests:
	@python -m pytest -s --cov=greensenti tests/