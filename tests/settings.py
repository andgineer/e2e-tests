class Config:
    # host can be overriden by pytest command line option '--host' (see conftest.py)
    host = 'http://www.python.org'  # Use host.docker.internal to go to local host from selenium grid docker
    api_host = 'https://localhost/api'
    webdriver_host = 'http://localhost:4444/wd/hub'
    local_screenshot_folder = 'screenshots'


config = Config()
