#!/bin/bash
#
# Wait for the Selenium Grid to be up and running
#

SELENIUM_GRID_URL="http://localhost:4444"

set -e
cmd="$@"

while ! curl -sSL "${SELENIUM_GRID_URL}/wd/hub/status" 2>&1 \
        | jq -r '.value.ready' 2>&1 | grep "true" >/dev/null; do
    echo "Waiting for the Selenium Grid at ${SELENIUM_GRID_URL}"
    sleep 1
done

>&2 echo "Selenium Grid is up and running at ${SELENIUM_GRID_URL}"
exec $cmd
