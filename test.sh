#!/usr/bin/env bash
#
# Run all end-to-end tests
# To filter by test name use test.sh -k <test name>
# To filter by test marks use test.sh -m "mark1 and mark2"

python -m pytest --alluredir=allure-results $@