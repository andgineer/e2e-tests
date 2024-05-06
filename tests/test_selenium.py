import allure
from webdriver_augmented import Page


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
