[![Github CI Status](https://github.com/andgineer/e2e-tests/workflows/ci/badge.svg)](https://github.com/andgineer/e2e-tests/actions)

# End-to-End Web UI Testing Framework

A robust end-to-end testing solution that runs tests in Chrome, Firefox, and Microsoft Edge 
using headless browsers and Selenium Grid in Docker Compose. 

Features beautiful test reporting powered by [Allure](https://github.com/allure-framework/allure2).

For detailed implementation insights, check out my [blog post](https://sorokin.engineer/posts/en/e2e_tests.html).

## Test Reporting

This framework generates comprehensive Allure reports:

![Allure Report Example](/img/allure-report.png)

When running on GitHub Actions, reports are automatically published to GitHub Pages: [View Latest Test Results](https://andgineer.github.io/e2e-tests/builds/tests/)

## Getting Started

### Setup

Launch Allure Server and Selenium Grid:

    docker-compose up -d

The Allure reports will be available at `http://localhost:8800`, 
and the Selenium Grid console at `http://localhost:4444/ui/`.

The Selenium Grid is started automatically by the tests (see `setup_selenium_grid()` in `conftest.py`), 
but manually launching it in the background with docker-compose makes tests faster since they don't need to start 
and stop the Grid for each test run.

### Multiple Project Setup

When using Selenium Grid across multiple projects, you may encounter port conflicts:

    Bind for 0.0.0.0:4442 failed: port is already allocated

This happen if the Selenium Grid is already running.

In such cases, start Docker Compose without Selenium Grid:

    docker-compose up -d  --scale hub=0

## Running Tests

### Prerequisites

1. Install dependencies:

   . ./activate.sh

2. Run tests and generate reports:

   scripts/test.sh

Tests store results in the `allure-results` folder, which is mounted to the Allure reporter Docker container.

Tests run in parallel in Chrome, Firefox, and Microsoft Edge browsers with pytest fixture `browser`.

### Testing Custom URLs

The framework supports testing any web application via the `--host` parameter. For example:

    scripts/test.sh --host=https://google.com

The `--host` parameter is implemented using [pytest's hook pytest_addoption](https://docs.pytest.org/en/latest/how-to/writing_hook_functions.html#using-hooks-in-pytest-addoption) in `conftest.py`.

Note: The Google example above will fail as it expects to find the word "Python" on the main page.