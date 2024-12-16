#!/bin/bash

# Activate conda environment if it exists
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    conda activate quantum-env
fi

# Add the project root to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the TUI
python -m services.cortex.ui.quantum_tui
