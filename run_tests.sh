#!/bin/bash
# run_tests.sh - Provision a venv, ensure a stackql binary, then run the full
# PyStackQL test suite (local + server) on Linux/macOS and print a summary.
#
# Steps:
#   1. Create/activate a Python venv and install dependencies (this process only)
#   2. Ensure a stackql binary exists in the current directory (download if not)
#   3. Start the stackql server
#   4. Run the local tests   (run_tests.py)
#   5. Run the server tests  (run_server_tests.py)
#   6. Stop the stackql server
#   7. Print a PASS/FAIL summary with totals
#
# This is for bash on Linux/macOS. On Windows use the PowerShell workflow.

# Use simpler output without colors when not running under bash
if [ -n "$BASH_VERSION" ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    cecho() {
        printf "%b%s%b\n" "$1" "$2" "$NC"
    }
else
    cecho() {
        echo "$2"
    }
fi

# Configuration
VENV_NAME=".venv"
REQUIREMENTS_FILE="requirements.txt"
LOCAL_RUNNER="run_tests.py"
SERVER_RUNNER="run_server_tests.py"
START_SERVER_SCRIPT="start-stackql-server.sh"
STOP_SERVER_SCRIPT="stop-stackql-server.sh"
STACKQL_INSTALLER="https://get-stackql.io/install"

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Extract the pytest summary line (e.g. "43 passed, 1 skipped") from a log file
extract_summary() {
    grep -aE '(passed|failed|error|no tests ran)' "$1" \
        | tail -1 \
        | sed -E 's/=+//g; s/in [0-9.]+s//; s/^[[:space:]]+//; s/[[:space:]]+$//'
}

# Banner
cecho "$BLUE" "======================================="
cecho "$BLUE" "  PyStackQL Test Runner                "
cecho "$BLUE" "======================================="
echo ""

# --- 1. Python venv setup -------------------------------------------------

if ! command_exists python3; then
    cecho "$RED" "Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

cecho "$YELLOW" "Using Python:"
python3 --version
echo ""

if [ ! -d "$VENV_NAME" ]; then
    cecho "$YELLOW" "Creating virtual environment in ${VENV_NAME}..."
    python3 -m venv "$VENV_NAME"
    if [ $? -ne 0 ]; then
        cecho "$RED" "Error: Failed to create virtual environment."
        exit 1
    fi
    cecho "$GREEN" "Virtual environment created successfully."
else
    cecho "$YELLOW" "Using existing virtual environment in ${VENV_NAME}"
fi

# macOS/Linux activation path
ACTIVATE_SCRIPT="$VENV_NAME/bin/activate"
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    cecho "$RED" "Error: Activation script not found at $ACTIVATE_SCRIPT"
    echo "The virtual environment may be corrupt. Remove $VENV_NAME and re-run."
    exit 1
fi

cecho "$YELLOW" "Activating virtual environment..."
. "$ACTIVATE_SCRIPT"
if [ $? -ne 0 ]; then
    cecho "$RED" "Error: Failed to activate virtual environment."
    exit 1
fi

cecho "$YELLOW" "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel >/dev/null
if [ $? -ne 0 ]; then
    cecho "$RED" "Warning: Failed to upgrade pip, setuptools, or wheel. Continuing anyway."
fi

if [ -f "$REQUIREMENTS_FILE" ]; then
    cecho "$YELLOW" "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE" >/dev/null
    if [ $? -ne 0 ]; then
        cecho "$RED" "Warning: Some dependencies may have failed to install."
    else
        cecho "$GREEN" "Dependencies installed successfully."
    fi
else
    cecho "$RED" "Warning: $REQUIREMENTS_FILE not found, skipping dependency install."
fi

if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    cecho "$YELLOW" "Installing PyStackQL in development mode..."
    pip install -e . >/dev/null
    if [ $? -ne 0 ]; then
        cecho "$RED" "Warning: Failed to install package in development mode."
    else
        cecho "$GREEN" "Package installed in development mode."
    fi
fi
echo ""

# --- 2. Ensure a stackql binary in the current directory ------------------

if [ -x "./stackql" ]; then
    cecho "$GREEN" "Found stackql binary: $(pwd)/stackql"
else
    cecho "$YELLOW" "No stackql binary in $(pwd), downloading..."
    curl -fsSL "$STACKQL_INSTALLER" | sh
    if [ ! -x "./stackql" ]; then
        cecho "$RED" "Error: stackql binary was not installed to $(pwd)."
        exit 1
    fi
    cecho "$GREEN" "stackql binary installed: $(pwd)/stackql"
fi
echo ""

# --- 3. Start the stackql server ------------------------------------------

# Always attempt to stop the server on exit so we don't leave it running.
trap 'bash "$STOP_SERVER_SCRIPT" >/dev/null 2>&1' EXIT

cecho "$BLUE" "Starting stackql server..."
bash "$START_SERVER_SCRIPT"
echo ""

# --- 4. Local tests -------------------------------------------------------

cecho "$BLUE" "======================================="
cecho "$BLUE" "  Running local tests ($LOCAL_RUNNER)"
cecho "$BLUE" "======================================="
LOCAL_LOG=$(mktemp)
python "$LOCAL_RUNNER" 2>&1 | tee "$LOCAL_LOG"
LOCAL_CODE=${PIPESTATUS[0]}
LOCAL_SUMMARY=$(extract_summary "$LOCAL_LOG")
rm -f "$LOCAL_LOG"
echo ""

# --- 5. Server tests ------------------------------------------------------

cecho "$BLUE" "======================================="
cecho "$BLUE" "  Running server tests ($SERVER_RUNNER)"
cecho "$BLUE" "======================================="
SERVER_LOG=$(mktemp)
python "$SERVER_RUNNER" 2>&1 | tee "$SERVER_LOG"
SERVER_CODE=${PIPESTATUS[0]}
SERVER_SUMMARY=$(extract_summary "$SERVER_LOG")
rm -f "$SERVER_LOG"
echo ""

# --- 6. Stop the stackql server -------------------------------------------

cecho "$BLUE" "Stopping stackql server..."
bash "$STOP_SERVER_SCRIPT"
trap - EXIT
echo ""

# --- 7. Summary -----------------------------------------------------------

if [ "$LOCAL_CODE" -eq 0 ]; then
    LOCAL_STATUS="${GREEN}PASS${NC}"
else
    LOCAL_STATUS="${RED}FAIL${NC}"
fi
if [ "$SERVER_CODE" -eq 0 ]; then
    SERVER_STATUS="${GREEN}PASS${NC}"
else
    SERVER_STATUS="${RED}FAIL${NC}"
fi

if [ "$LOCAL_CODE" -eq 0 ] && [ "$SERVER_CODE" -eq 0 ]; then
    OVERALL_STATUS="${GREEN}PASS${NC}"
    OVERALL_CODE=0
else
    OVERALL_STATUS="${RED}FAIL${NC}"
    OVERALL_CODE=1
fi

cecho "$BLUE" "======================================="
cecho "$BLUE" "  Test Summary                         "
cecho "$BLUE" "======================================="
printf "  %-14s %b  (%s)\n" "Local tests:"  "$LOCAL_STATUS"  "${LOCAL_SUMMARY:-no results}"
printf "  %-14s %b  (%s)\n" "Server tests:" "$SERVER_STATUS" "${SERVER_SUMMARY:-no results}"
cecho "$BLUE" "---------------------------------------"
printf "  %-14s %b\n" "Overall:" "$OVERALL_STATUS"
cecho "$BLUE" "======================================="

exit $OVERALL_CODE
