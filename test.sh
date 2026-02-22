#!/bin/bash

# Check if already in a virtual env
if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi
    echo "Activating virtual environment..."
    source .venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

echo "Running dataset generation..."
python data/generate_dataset.py

echo "Running dataset processing..."
python data/run_dataset.py

echo "Validating results..."
python data/validate_results.py

echo "Starting FastAPI server..."
python app/main.py
