install:
	@python setup.py install

version:
	@python -V

clean:
	@rm -rf build dist .eggs src/*.egg-info
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '.pytest_cache' -exec rm -rf {} +

black: clean
	@python -m isort --profile black src/ tests/
	@python -m black src/ tests/

lint:
	@python -m mypy greensenti/ tests/

release:
	@echo Bump version to v$$(poetry version --short)
	@git tag v$$(poetry version --short)
	@git push origin v$$(poetry version --short)

.PHONY: tests

tests:
	@python -m pytest -s tests/