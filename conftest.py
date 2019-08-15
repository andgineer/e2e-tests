"""
Config for py.test
"""
import os
import urllib
from datetime import datetime
import pytest
import allure
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import settings
from webdriver_augmented import WebDriverAugmented
import urllib3
import logging


log = logging.getLogger()

test_browsers = ['Chrome', 'Firefox']
browser_options = {
    'Chrome': ChromeOptions, # DesiredCapabilities.CHROME,
    'Firefox': FirefoxOptions,  # DesiredCapabilities.FIREFOX
}


def desired_caps(browser: str) -> DesiredCapabilities:
    options = browser_options[browser]()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--no-sandbox")
    caps = options.to_capabilities()
    caps['platform'] = 'Linux'
    return caps


def get_web_driver(browser: str) -> WebDriverAugmented:
    """
    Creates remote web driver (located on selenium host) for desired browser.
    """
    FAIL_HELP = f'''
    Fail to connect to selenium webdriver remote host {settings.config.webdriver_host}.

    To run local selenium hub from tests_e2e folder: 
        docker-compose up -d

    To restart freezing local selenium hub:
        restart_selenium.sh

    '''
    webdrv = None
    try:
        webdrv = WebDriverAugmented(
            command_executor=settings.config.webdriver_host,
            desired_capabilities=desired_caps(browser)
        )
        webdrv.page_timer.start()
    except WebDriverException as e:
        pytest.exit(FAIL_HELP + f':\n\n{e}\n')
    except urllib.error.URLError as e:
        pytest.exit(FAIL_HELP + f':\n\n{e}\n')
    except (urllib3.exceptions.ReadTimeoutError, urllib3.exceptions.NewConnectionError, urllib3.exceptions.MaxRetryError) as e:
        pytest.exit(FAIL_HELP + f':\n\n{e}\n')
    return webdrv


@pytest.fixture(scope='session', params=test_browsers, ids=lambda x: 'Browser: {}'.format(x))
def browser(request):
    """
    Returns all browsers to test with
    """
    webdrv = get_web_driver(request.param)
    request.addfinalizer(lambda *args: webdrv.quit())
    #driver.implicitly_wait(Config().WEB_DRIVER_IMPLICITE_WAIT)
    webdrv.maximize_window()
    return webdrv


def pytest_runtest_logstart(nodeid, location):
    """ signal the start of running a single test item.

    This hook will be called **before** :func:`pytest_runtest_setup`, :func:`pytest_runtest_call` and
    :func:`pytest_runtest_teardown` hooks.

    :param str nodeid: full id of the item
    :param location: a triple of ``(filename, linenum, testname)``
    """
    log.info('Test started')


def pytest_runtest_logfinish(nodeid, location):
    log.info('Test finished')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call' and rep.failed:
        mode = 'a' if os.path.exists('failures') else 'w'
        try:
            with open('failures', mode) as f:
                if 'browser' in item.fixturenames:  # assume this is fixture with webdriver
                    web_driver = item.funcargs['browser']
                else:
                    print('Fail to take screen-shot')
                    return
            allure.attach(
                web_driver.get_screenshot_as_png(),
                name='screenshot',
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(
                '\n'.join(web_driver.get_log('browser')),
                name='console log',
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as e:
            print('Fail to take screen-shot: {}'.format(e))


def pytest_addoption(parser):
    """
    py.test options
    """
    parser.addoption(
        '--host',
        type='string',
        default=settings.config.host,
        dest='host',
        help=f'''Base URL of the host to test. By default "{settings.config.host}". 
Use host.docker.internal to go to local host from selenium grid docker.''')


def pytest_report_header(config):
    return '{start} Host: {host} {stop}\n'.format(
        start='>' * 5,
        host=config.getoption('host'),
        stop='<' * 5
        )


def pytest_cmdline_main(config):
    """
    After command line is parsed
    """
    settings.config.host = config.getoption('host')
