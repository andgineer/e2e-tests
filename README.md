[![Github CI Status](https://github.com/andgineer/e2e-tests/workflows/ci/badge.svg)](https://github.com/andgineer/e2e-tests/actions)
## End-to-end web UI tests

Uses headless-browsers and Selenuim Grid in docker-compose.

Produce beautiful reports with [allure](https://github.com/allure-framework/allure2).

Read more in my [blog](https://sorokin.engineer/posts/en/e2e_tests.html).

#### Test report example:

![](/img/allure-report.png)

## Usage

To start Selenium Grid and Allure reporter run:

    docker-compose up -d

Your Selenium Grid console will be at `http://localhost:4444/ui`

Install dependencies (note: there are two dots):

    . ./activate.sh

To run all tests:

    scripts/test.sh

To test specific host:

    scripts/test.sh --host=<full URL>

The script save test results in folder `allure-results` mounted to the Allure reporter.
The reports are available at `http://localhost:4040`.
