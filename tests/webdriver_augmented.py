import logging
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support.ui import WebDriverWait
import time
import pprint
import urllib.parse
import settings
from pprint import pformat

PAGE_MAX_WAIT_TIME = 20  # second to wait for components
PAGE_STEP_SLEEP = 0.5  # seconds to delay in component waiting loop
FIRST_PAGE_MAX_WAIT_TIME = 20  # seconds to wait for components on first page
MAX_JS_LOG_SIZE = 1024  # longer js log truncated in error messages


logger = logging.getLogger()


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
        self._cdp_enabled = False
        self._log_entries = []
        super().__init__(*args, **kwargs)
        self._setup_cdp_logging()

    def _setup_cdp_logging(self):
        """Setup CDP logging for Chromium-based browsers"""
        try:
            if hasattr(self, 'caps') and self.caps.get('browserName', '').lower() == 'msedge':
                # Edge requires a different CDP command path
                self.command_executor._commands.update({
                    'executeCdpCommand': ('POST', '/session/$sessionId/ms/cdp/execute'),
                    'getCdpConnection': ('GET', '/session/$sessionId/ms/cdp/connection')
                })

            self.execute_cdp_cmd("Runtime.enable", {})
            self._cdp_enabled = True
            # Inject error capture script
            self._inject_error_capture()
        except Exception:
            self._cdp_enabled = False

    def _inject_error_capture(self):
        """Inject JavaScript to capture console errors"""
        if not self._cdp_enabled:
            return

        script = """
        (function() {
            if (window.__selenium_logs) return; // Already injected
            
            window.__selenium_logs = [];
            window.__selenium_logs_ready = false;

            // Capture console.error
            const originalError = console.error;
            console.error = function(...args) {
                window.__selenium_logs.push({
                    level: 'SEVERE',
                    message: args.map(a => String(a)).join(' '),
                    timestamp: Date.now()
                });
                originalError.apply(console, args);
            };

            // Capture console.warn
            const originalWarn = console.warn;
            console.warn = function(...args) {
                window.__selenium_logs.push({
                    level: 'WARNING',
                    message: args.map(a => String(a)).join(' '),
                    timestamp: Date.now()
                });
                originalWarn.apply(console, args);
            };

            // Capture console.log
            const originalLog = console.log;
            console.log = function(...args) {
                window.__selenium_logs.push({
                    level: 'INFO',
                    message: args.map(a => String(a)).join(' '),
                    timestamp: Date.now()
                });
                originalLog.apply(console, args);
            };

            // Capture uncaught errors
            window.addEventListener('error', function(e) {
                window.__selenium_logs.push({
                    level: 'SEVERE', 
                    message: e.message + ' at ' + e.filename + ':' + e.lineno,
                    timestamp: Date.now()
                });
            });
            
            // Capture unhandled promise rejections
            window.addEventListener('unhandledrejection', function(e) {
                window.__selenium_logs.push({
                    level: 'SEVERE',
                    message: 'Unhandled promise rejection: ' + e.reason,
                    timestamp: Date.now()
                });
            });

            window.__selenium_logs_ready = true;
        })();
        """
        try:
            self.execute_script(script)
        except Exception as e:
            logger.error(f"Failed to inject error capture: {e}")

    def get_log(self, log_type="browser"):
        """Get JavaScript console log entries.
        
        (!) Note: clears the log.
        """
        if not self._cdp_enabled or log_type != "browser":
            return []

        try:
            result = self.execute_script("""
                if (window.__selenium_logs) {
                    const logs = [...window.__selenium_logs];
                    window.__selenium_logs = [];
                    return logs;
                }
                return [];
            """)    
        except Exception as e:
            logger.warning(f"Failed to get browser logs: {e}")
            result = []
        if result:
            logger.warning(f"js log {len(result)} error entries found")
        return result
        
    def get(self, url):
        """Override get to ensure log capture is maintained after navigation."""
        super().get(url)
        # Wait for page load
        WebDriverWait(self, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        # Re-inject log capture
        self._inject_error_capture()

    def goto(self, page: str):
        """
        Open the page (see class Page).
        """
        self.get(urllib.parse.urljoin(settings.config.host, page))

    @staticmethod
    def check_js_log(js_log: list[dict[str, Any]]) -> bool:
        """Check java script log for errors (only `severe` level)."""
        critical_errors = []
        total_chars = 0
        idx = 0
        for entry in js_log:
            if entry['level'] in ['SEVERE']:
                idx += 1
                critical_errors.append(entry)
                total_chars += len(entry['message'])
                if total_chars >= MAX_JS_LOG_SIZE:
                    critical_errors.append('<...>')
                    break
        if critical_errors:
            print(f'js log errors: \n{pprint.pformat(critical_errors, indent=4)}')
        return not critical_errors
    