[![Github CI Status](https://github.com/andgineer/e2e-tests/workflows/ci/badge.svg)](https://github.com/andgineer/e2e-tests/actions)
## End-to-end web UI tests

Uses headless-browsers and Selenuim Grid in docker-compose.

Produce beautiful reports with [allure](https://github.com/allure-framework/allure2).

Read more in my [blog](https://sorokin.engineer/posts/en/e2e_tests.html).

## Allure test report
- Test report example: ![](/img/allure-report.png)
- when run on GitHub Actions, an Allure report is created and uploaded on github pages: [Allure report](https://andgineer.github.io/e2e-tests/builds/tests/)

## Usage

To start Selenium Grid and Allure reporter run:

    docker-compose up -d

Your Selenium Grid console will be at `http://localhost:4444/ui/`.

The reports are available at `http://localhost:8800`.

#### Run tests

Tests should save results in folder `allure-results` mounted 
to the Docker container with Allure reporter.

Install dependencies (note: there are two dots), 
run all tests from `tests` folder and create allure report:

    . ./activate.sh
    scripts/test.sh

Our tests have a parameter `--host` to specify the URL of 
the tested web application - see 
[pytest hook pytest_addoption](https://docs.pytest.org/en/latest/how-to/writing_hook_functions.html#using-hooks-in-pytest-addoption)
in conftest.py. 

For example, to test `https://google.com` run:

    scripts/test.sh --host=https://google.com

This will fail because there is no word "Python" on 
the Google main page, unfortunately.


