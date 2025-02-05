black:
	poetry run black .

isort:
	poetry run isort .

format: isort black

make run:
	poetry run uvicorn src.app:app --reload

type-check:
	poetry run mypy .

lint:
	poetry run ruff check .

fix-lint:
	poetry run ruff check . --fix

e2e-test:
	poetry run python -m pytest