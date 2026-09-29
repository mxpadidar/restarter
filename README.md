# restarter

A Django REST Framework template for starting a new API. It includes account
authentication, role-based permissions, and a small set of working endpoints.

## What's included

- Signup, login, logout, refresh-token rotation, profile, and admin-only user listing.
- JWT access tokens, rotating refresh grants, and role-based API permissions.
- Structured API errors, request IDs, logging, and OpenAPI docs.
- Tests, Ruff, and Pyright. SQLite is configured for local development.

## Get started

Requires Python 3.14+, Django 6.1.1+, and [uv](https://docs.astral.sh/uv/).
Create a repository from this template, then run:

```sh
uv sync
cp .env.example .env
uv run manage.py migrate
uv run manage.py runserver
```

The API is under `/api/accounts/`. Visit the [API docs](http://127.0.0.1:8000/docs/)
to explore its routes; `/health/` is a simple health check.

For your own project, change the project name in `pyproject.toml`, set `app_name`
in `.env`, and replace the example secrets. Review the allowed hosts and database
settings before deploying.

## Checks

```sh
make all
```

`make all` syncs dependencies, formats and lints, checks types and migrations, and runs tests.
