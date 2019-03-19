from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
import time
import pprint
import urllib.parse
import settings
import pytest


PAGE_MAX_WAIT_TIME = 20  # second to wait for components
PAGE_STEP_SLEEP = 0.5  # seconds to delay in component waiting loop
FIRST_PAGE_MAX_WAIT_TIME = 20  # seconds to wait for components on first page
MAX_JS_LOG_SIZE = 1024  # longer js log truncated in error messages


class PageTimer():
    """Count down timer для ожиданий с timeout.
    """
    first_page = True
    max_time = time.monotonic()# + FIRST_PAGE_MAX_WAIT_TIME

    def start(self):
        if self.first_page:
            self.max_time = time.monotonic() + FIRST_PAGE_MAX_WAIT_TIME
            self.first_page = False
        else:
            self.max_time = time.monotonic() + PAGE_MAX_WAIT_TIME

    def time_is_up(self):
        return time.monotonic() >= self.max_time

    def sleep(self):
        time.sleep(PAGE_STEP_SLEEP)

    def time_to_wait(self):
        return self.max_time - time.monotonic()


class Page:
    root = ''
    projects = 'projects'


class WebDriverAugmented(RemoteWebDriver):
    """
    Web driver, augmented with application specific logic.
    """
    def __init__(self, *args, **kwargs):
        self.page_timer = PageTimer()
        self.need_refresh = False
        super().__init__(*args, **kwargs)

    def goto(self, page: str):
        """
        Open the page (see class Page).
        """
        self.get(urllib.parse.urljoin(pytest.config.getoption('host'), page))

    def check_js_log(self):
        """
        check java script log for errors (only `severe` level)
        """
        js_log = self.get_log("browser")
        clean_log = []
        total_chars = 0
        idx = 0
        for entry in js_log:
            if entry['level'] in ['SEVERE']:
                idx += 1
                clean_log.append(entry)
                total_chars += len(entry['message'])
                if total_chars >= MAX_JS_LOG_SIZE:
                    clean_log.append('<...>')
                    break
        assert len(clean_log) == 0, 'js log errors: \n{}'.format(pprint.pformat(clean_log, indent=4))

