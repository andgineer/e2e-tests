import allure
import pytest
from webdriver_augmented import Page


@pytest.mark.skip_js_errors
@allure.epic('End-to-end test suit')
@allure.feature('Selenium')
@allure.story('Test selenium grid is alive')
@allure.issue('https://github.com/andgineer/api-db-prototype/issues/1')
@allure.testcase('https://github.com/andgineer/api-db-prototype/issues/2')
def test_selenium(browser):
    """
    Test that test infrastructure (selenium grid, allure reporter) is working
    """
    with allure.step('Test access to python.org'):
        browser.goto(Page.root)
        assert "Python" in browser.title
    with allure.step('Taking screenshot'):
        allure.attach(
              browser.get_screenshot_as_png(),
              name='screenshot',
              attachment_type=allure.attachment_type.PNG
        )
    with allure.step('Generate JavaScript errors (will be logged but not fail the test because of mark.skip_js_errors)'):
        browser.execute_script("console.error('Test console error - should not fail the test');")
        browser.execute_script("console.warn('Test console warn - should not fail the test');")
        browser.execute_script("console.log('Test console log - should not fail the test');")

