install:
	@poetry install

clean:
	@rm -rf build dist .eggs *.egg-info
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +

black: clean
	@poetry run isort --profile black greensenti/
	@poetry run black greensenti/

lint:
	@poetry run mypy greensenti/

.PHONY: tests

tests:
	@poetry run python -m unittest discover -s tests/ --quiet