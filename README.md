[![Build Status](https://travis-ci.org/masterandrey/e2e-tests.png)](https://travis-ci.org/masterandrey/e2e-tests)
## End-to-end web UI tests

Uses headless-browsers with local Selenuim Grid server.

And [allure](https://github.com/allure-framework/allure2) web-report generator.

Use `setup.sh` to prepare for tests.
 
To start Selenium Grid and Allure reporter run:

    docker-compose up -d
    
Do not forget to start the server under test if you run it locally.
    
To run all tests:

    test.sh

Creates web-report on http://localhost:4040 .

To test non-default (not local) host:

    test.sh --host=<full URL>
    
### MacOS

Remove `extra_hosts` from docker-compose.yaml because Docker for MacOS define the name internally.      

![](/img/allure-report.png)
