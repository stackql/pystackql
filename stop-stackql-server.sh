#!/bin/bash
# Stop the stackql server started by start-stackql-server.sh.
# Match the 'srv' invocation specifically so we don't kill unrelated processes
# that merely have "stackql" in their command line (e.g. a repo path that
# contains "stackql", or the test runner itself).
PID=$(pgrep -f "stackql.*srv")

if [ -z "$PID" ]; then
    echo "stackql server is not running."
else
    echo "stopping stackql server (PID: $PID)..."
    kill $PID
    echo "stackql server stopped."
fi
