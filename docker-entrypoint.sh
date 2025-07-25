#!/bin/bash

# Start Xvfb for headless operation
Xvfb :99 -screen 0 1920x1080x24 &

# Wait for Xvfb to start
sleep 2

# Start the Flask application
python app.py
