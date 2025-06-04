#!/bin/bash
# launch_venv.sh - Script to create, set up and activate a Python virtual environment for PyStackQL

# Use simpler code without colors when running with sh
if [ -n "$BASH_VERSION" ]; then
    # Color definitions for bash
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    
    # Function to print colored text in bash
    cecho() {
        printf "%b%s%b\n" "$1" "$2" "$NC"
    }
else
    # No colors for sh
    cecho() {
        echo "$2"
    }
fi

# Default virtual environment name
VENV_NAME=".venv"
REQUIREMENTS_FILE="requirements.txt"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Banner
cecho "$BLUE" "======================================="
cecho "$BLUE" "  PyStackQL Development Environment   "
cecho "$BLUE" "======================================="
echo ""

# Check for Python
if ! command_exists python3; then
    cecho "$RED" "Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Print Python version
cecho "$YELLOW" "Using Python:"
python3 --version
echo ""

# Create virtual environment if it doesn't exist
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

# Determine the activate script based on OS
case "$OSTYPE" in
    msys*|win*|cygwin*)
        # Windows
        ACTIVATE_SCRIPT="$VENV_NAME/Scripts/activate"
        ;;
    *)
        # Unix-like (Linux, macOS)
        ACTIVATE_SCRIPT="$VENV_NAME/bin/activate"
        ;;
esac

# Check if activation script exists
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    cecho "$RED" "Error: Activation script not found at $ACTIVATE_SCRIPT"
    echo "The virtual environment may be corrupt. Try removing the $VENV_NAME directory and running this script again."
    exit 1
fi

# Source the activation script
cecho "$YELLOW" "Activating virtual environment..."
. "$ACTIVATE_SCRIPT"
if [ $? -ne 0 ]; then
    cecho "$RED" "Error: Failed to activate virtual environment."
    exit 1
fi

# Install/upgrade pip, setuptools, and wheel
cecho "$YELLOW" "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    cecho "$RED" "Warning: Failed to upgrade pip, setuptools, or wheel. Continuing anyway."
fi

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    cecho "$RED" "Error: $REQUIREMENTS_FILE not found."
    echo "Please make sure the file exists in the current directory."
    cecho "$YELLOW" "Continuing with an activated environment without installing dependencies."
else
    # Install requirements
    cecho "$YELLOW" "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        cecho "$RED" "Warning: Some dependencies may have failed to install."
    else
        cecho "$GREEN" "Dependencies installed successfully."
    fi
fi

# Install the package in development mode if setup.py exists
if [ -f "setup.py" ]; then
    cecho "$YELLOW" "Installing PyStackQL in development mode..."
    pip install .
    if [ $? -ne 0 ]; then
        cecho "$RED" "Warning: Failed to install package in development mode."
    else
        cecho "$GREEN" "Package installed in development mode."
    fi
fi

# Success message
echo ""
cecho "$GREEN" "Virtual environment is now set up and activated!"
cecho "$YELLOW" "You can use PyStackQL and run tests."
echo ""
cecho "$BLUE" "To run tests:"
echo "  python run_tests.py"
echo ""
cecho "$BLUE" "To deactivate the virtual environment when done:"
echo "  deactivate"
echo ""
cecho "$BLUE" "======================================="

# Keep the terminal open with the activated environment
# The script will be source'd, so the environment stays active
exec "${SHELL:-bash}"