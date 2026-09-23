.PHONY: all install run migrations migrate superuser ruff type-check test

all: install ruff type-check test
	@echo "-> all checks passed!"

install:
	@echo "-> syncing dependencies..."
	@uv sync --quiet

run:
	@echo "-> starting development server..."
	@uv run manage.py runserver

migrations:
	@echo "-> creating migrations..."
	@uv run manage.py makemigrations

migrate:
	@echo "-> applying migrations..."
	@uv run manage.py migrate

superuser:
	@echo "-> creating superuser..."
	@uv run manage.py createsuperuser

ruff:
	@echo "-> formatting and linting..."
	@uv run ruff format . --quiet
	@uv run ruff check . --quiet

type-check:
	@echo "-> type checking..."
	@uv run pyright .

test:
	@echo "-> running tests..."
	@uv run pytest
