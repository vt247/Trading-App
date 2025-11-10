#!/bin/bash
# Render.com startup script for Wolf Market Analyzer

# Change to the project directory
cd /opt/render/project/src

# Run the web dashboard
python web_dashboard.py --host 0.0.0.0 --port $PORT
