APP_ROOT=app
RUN_CMD=uv run

lint-check:
	$(RUN_CMD) ruff check $(APP_ROOT)

lint-fix:
	$(RUN_CMD) ruff check --fix $(APP_ROOT)

format-check:
	$(RUN_CMD) ruff format --check $(APP_ROOT)

format-fix:
	$(RUN_CMD) ruff format $(APP_ROOT)

mypy-check:
	$(RUN_CMD) mypy --show-traceback $(APP_ROOT)


check: lint-check format-check mypy-check
fix: format-fix lint-fix