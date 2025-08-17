# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an end-to-end testing framework using Selenium Grid with pytest, designed to run automated tests across multiple browsers (Chrome, Firefox, Edge) using headless browsers in Docker containers. The framework generates beautiful test reports using Allure and includes comprehensive JavaScript error logging and screenshot capture on test failures.

## Common Commands

### Environment Setup
```bash
# Activate virtual environment and install dependencies
. ./activate.sh
```

### Test Execution
```bash
# Run all tests with Allure reporting
scripts/test.sh

# Run tests with filters
scripts/test.sh -k "test_name"           # Filter by test name
scripts/test.sh -m "mark1 and mark2"     # Filter by test marks

# Test custom URLs
scripts/test.sh --host=https://example.com
```

### Docker Services
```bash
# Start Selenium Grid and Allure server
docker compose up -d

# Start without Selenium Grid (if port conflicts occur)
docker compose up -d --scale hub=0

# View Allure reports at http://localhost:8800
# View Selenium Grid console at http://localhost:4444/ui/
```

## Architecture

### Test Infrastructure
- **Selenium Grid**: Multi-browser testing environment running in Docker
- **WebDriverAugmented**: Custom WebDriver wrapper with enhanced JavaScript logging via Chrome DevTools Protocol (CDP)
- **Allure Integration**: Comprehensive test reporting with screenshots and log attachments
- **Browser Support**: Chrome, Firefox, and Microsoft Edge with headless execution

### Key Components

#### WebDriverAugmented (`tests/webdriver_augmented.py`)
Enhanced Selenium WebDriver with:
- CDP-based JavaScript console logging for all log levels (error, warn, info)
- Automatic error capture for uncaught exceptions and promise rejections
- Edge browser CDP compatibility handling
- Page timing and navigation utilities

#### Test Configuration (`tests/conftest.py`)
- Session-scoped Selenium Grid auto-startup
- Browser fixture with parallel execution across all supported browsers
- JavaScript error checking with `@pytest.mark.skip_js_errors` marker
- Automatic screenshot capture on test failures
- Docker host IP detection for cross-platform compatibility

#### Settings (`tests/settings.py`)
Centralized configuration with customizable host URLs via `--host` command line option.

### Test Execution Flow
1. Session fixture starts Selenium Grid if not running
2. Browser fixture creates WebDriver instances for each browser
3. Tests run in parallel across all browsers
4. JavaScript logs are captured and attached to Allure reports
5. Screenshots are automatically taken on failures
6. Allure generates comprehensive HTML reports

## Development Notes

- Tests automatically fail on JavaScript SEVERE errors unless marked with `@pytest.mark.skip_js_errors`
- Use `WebDriverAugmented.goto(Page.root)` for navigation relative to configured host
- All console outputs (log, warn, error) are captured and attached to test reports
- Browser logs are cleared after each retrieval to prevent memory accumulation
- Docker Compose services include proper shared memory configuration for browser stability