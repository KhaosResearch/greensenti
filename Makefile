install:
	@poetry install

clean:
	@rm -rf build dist .eggs *.egg-info
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +

black: clean
	@poetry run isort --profile black greensenti/ workflow.py
	@poetry run black greensenti/ workflow.py

lint:
	@poetry run mypy greensenti/

release:
	@git tag v$$(poetry version --short) 2>/dev/null || echo 'Version already released, update your version!'
#	@git push origin v$$(poetry version --short)

.PHONY: tests

tests:
	@poetry run python -m unittest discover -s tests/ --quiet