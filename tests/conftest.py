"""
Config for py.test
"""
import platform
import socket
import subprocess
import time

import pytest
import allure
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options
import settings
from webdriver_augmented import WebDriverAugmented
import urllib3.exceptions
import logging


log = logging.getLogger()

CHROME_BROWSER_NAME = 'Chrome'
FIREFOX_BROWSER_NAME = 'Firefox'
EDGE_BROWSER_NAME = 'Edge'  # for the moment no support for Edge: https://github.com/andgineer/e2e-tests/issues/4

test_browsers = [CHROME_BROWSER_NAME, FIREFOX_BROWSER_NAME, EDGE_BROWSER_NAME]
browser_options = {
    CHROME_BROWSER_NAME: ChromeOptions,
    FIREFOX_BROWSER_NAME: FirefoxOptions,
    EDGE_BROWSER_NAME: EdgeOptions,
}


def is_docker_compose_running(service_name: str) -> bool:
    """Check if a Docker service is running."""
    try:
        result = subprocess.run(
            ['docker-compose', 'ps', '-q', service_name],
            stdout=subprocess.PIPE, text=True, check=True
        )
        # If the service is running, it will return its container ID thanks to the '-q' flag
        return result.stdout.strip() != ''
    except subprocess.CalledProcessError as e:
        print(f"Failed to check docker-compose service `{service_name}` status: {e}")
        return False


def start_docker_compose():
    """Starts the docker-compose services and logs output directly."""
    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print("Docker Compose started successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed to start Docker Compose.")
        print(e.stdout)
        print(e.stderr)
        raise RuntimeError("Docker Compose failed to start") from e


@pytest.fixture(scope="session", autouse=True)
def setup_selenium_grid():
    """Start Selenium Grid using Testcontainers if not already running."""
    service_name = "hub"
    if not is_docker_compose_running(service_name):
        start_docker_compose()
    yield


def get_options(browser: str) -> Options:
    options = browser_options[browser]()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--no-sandbox")
    options.add_argument('--headless')
    return options


def get_web_driver(browser_name: str, retry_interval=2, timeout=60) -> WebDriverAugmented:
    """
    Creates remote web driver (located on selenium host) for desired browser.
    """
    FAIL_HELP = f'''
    Fail to connect to selenium webdriver remote host {settings.config.webdriver_host}.

    To run local selenium hub from tests_e2e folder: 
        docker-compose up -d
    '''
    end_time = time.time() + timeout
    while True:
        try:
            webdrv = WebDriverAugmented(
                command_executor=settings.config.webdriver_host,
                options=get_options(browser_name),
            )
            webdrv.browser_name = browser_name
            webdrv.page_timer.start()
            return webdrv
        except urllib3.exceptions.ProtocolError as e:
            if time.time() >= end_time:
                pytest.exit(f'{FAIL_HELP}\n\n{e}\n')
            print(f"Connection failed: {e}. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
        except WebDriverException as e:
            pytest.exit(f'{FAIL_HELP}:\n\n{e}\n')
        except (urllib3.exceptions.ReadTimeoutError, urllib3.exceptions.NewConnectionError, urllib3.exceptions.MaxRetryError) as e:
            pytest.exit(f'{FAIL_HELP}:\n\n{e}\n')


@pytest.fixture(scope='session', params=test_browsers, ids=lambda x: f'Browser: {x}')
def browser(request):
    """
    Returns all browsers to test with
    """
    webdrv = get_web_driver(request.param)
    request.addfinalizer(lambda *args: webdrv.quit())
    # driver.implicitly_wait(Config().WEB_DRIVER_IMPLICITE_WAIT)
    webdrv.maximize_window()
    return webdrv


def get_docker_host_ip():
    """Get the IP address of the host accessible from within Docker containers.

    So we can test servers running on the host machine from the Selenium Hub.
    """
    if platform.system() == "Darwin":
        return "host.docker.internal"
    elif platform.system() == "Linux":
        return get_linux_docker_host_ip()
    else:
        raise RuntimeError("Unsupported platform")


def get_linux_docker_host_ip():
    """ Determine the IP address accessible from within Docker containers on Linux.

    Get the default gateway address.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1))  # Use a temporary connection to an external IP
            host_ip = s.getsockname()[0]
        return host_ip
    except socket.error as e:
        raise RuntimeError(f"Failed to determine host IP address: {e}") from e


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
        try:
            if 'browser' in item.fixturenames:  # assume this is fixture with webdriver
                web_driver = item.funcargs['browser']
            else:
                print('Fail to take screen-shot: no `browser` fixture')
                return
            allure.attach(
                web_driver.get_screenshot_as_png(),
                name='screenshot',
                attachment_type=allure.attachment_type.PNG
            )
            if web_driver.browser_name != FIREFOX_BROWSER_NAME:
                # Firefox do not support js logs: https://github.com/SeleniumHQ/selenium/issues/2972
                allure.attach(
                    '\n'.join(web_driver.get_log('browser')),
                    name='js console log:',
                    attachment_type=allure.attachment_type.TEXT,
                )

        except Exception as e:
            print(f'Fail to take screen-shot: {e}')


def pytest_addoption(parser):
    """
    py.test options
    """
    parser.addoption(
        '--host',
        type=str,
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
