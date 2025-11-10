#!/bin/bash
# Render.com startup script for Wolf Market Analyzer

# Set Python path to find src modules
export PYTHONPATH=/opt/render/project/src

# Change to the correct directory
cd /opt/render/project/src

# Run the web dashboard
python web_dashboard.py --host 0.0.0.0 --port $PORT
