#!/bin/bash
# Dessertable - Easy Startup Script for Mac/Linux
# Run this script to launch the application

echo "========================================"
echo "Dessertable - Launcher"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Please make sure Python 3 is installed"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "Checking dependencies..."
pip show Flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Launch the GUI launcher
echo ""
echo "Starting Dessertable GUI Launcher..."
echo ""
python launcher.py

# If launcher exits, deactivate venv
deactivate
