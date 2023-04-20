[![Github CI Status](https://github.com/andgineer/e2e-tests/workflows/ci/badge.svg)](https://github.com/andgineer/e2e-tests/actions)
## End-to-end web UI tests

Uses headless-browsers with local Selenuim Grid server.

And [allure](https://github.com/allure-framework/allure2) web-report generator.

Read more in my [blog](https://sorokin.engineer/posts/en/e2e_tests.html).

To start Selenium Grid and Allure reporter run:

    docker-compose up -d

Your Selenium Grid console will be at `http://localhost:4444/ui`

To run all tests:

    scripts/test.sh

To test specific host:

    scripts/test.sh --host=<full URL>

Creates web-report on `http://localhost:4040` . 

### Test report example:

![](/img/allure-report.png)
