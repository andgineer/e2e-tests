[![Build Status](https://travis-ci.org/andgineer/e2e-tests.png)](https://travis-ci.org/andgineer/e2e-tests)
[![Github CI Status](https://github.com/andgineer/e2e-tests/workflows/ci/badge.svg)](https://github.com/andgineer/e2e-tests/actions)
## End-to-end web UI tests

Uses headless-browsers with local Selenuim Grid server.

And [allure](https://github.com/allure-framework/allure2) web-report generator.

Read more in my [blog](https://sorokin.engineer/posts/en/e2e_tests.html).

To start Selenium Grid and Allure reporter run:

    docker-compose up -d
    
To run all tests:

    test.sh

To test specific host:

    test.sh --host=<full URL>

Creates web-report on `http://localhost:4040` .
    
### MacOS

Remove `extra_hosts` from docker-compose.yaml because Docker for MacOS defines the name internally.      

### Test report example:

![](/img/allure-report.png)
