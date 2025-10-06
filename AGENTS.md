# Repository Guidelines

## Project Structure & Module Organization
- `tests/` holds the pytest suite, browser fixtures, and shared helpers such as `webdriver_augmented.py` and `settings.py`.
- `scripts/` contains task wrappers; `test.sh` orchestrates pytest, Allure report generation, and container restarts.
- `activate.sh` bootstraps a local virtual environment with Astral UV and ensures `allure-results/` exists.
- `docker-compose.yml` defines Selenium Grid, browser nodes, and the Allure service; keep it in sync with any infrastructure tweaks.

## Build, Test, and Development Commands
- `. ./activate.sh` — create or activate the `.venv` using UV and install Python dependencies listed in `requirements.txt`.
- `docker compose up -d` — start Selenium Grid and the Allure reporter locally; add `--scale hub=0` when sharing a Grid across projects.
- `scripts/test.sh` — run pytest against Chrome, Firefox, and Edge, collect results into `allure-results/`, and regenerate the Allure HTML report.
- `scripts/test.sh --host=https://target.example` — point tests at a different host via the `--host` option wired in `conftest.py`.

## Coding Style & Naming Conventions
- Follow standard PEP 8: four-space indentation, snake_case module and function names, CapWords classes, and descriptive pytest fixture names.
- Keep test functions named `test_*`; group scenarios with Allure decorators (`@allure.story`, `@pytest.mark.<tag>`) for report clarity.
- Log setup logic through helper functions rather than inline shell calls; prefer explicit waits over magic sleeps.

## Testing Guidelines
- Place new end-to-end coverage in `tests/`; share browser helpers through `webdriver_augmented.py` instead of duplicating Selenium calls.
- Use the session-scoped `browser` fixture for cross-browser runs and keep steps wrapped in `allure.step` blocks with meaningful attachment names.
- When extending configuration, expose defaults in `tests/settings.py` and document overrides in the PR.
- Verify report output locally before pushing by opening the regenerated Allure dashboard at `http://localhost:8800`.

## Commit & Pull Request Guidelines
- Mirror the existing history: concise, imperative, lower-case commit subjects such as `adapt to new allure version`.
- Reference related issues in Allure metadata or PR descriptions; include a brief risk summary when touching Selenium or Docker settings.
- Before requesting review, run `scripts/test.sh` and note the Allure report link or key screenshots in the PR body.
