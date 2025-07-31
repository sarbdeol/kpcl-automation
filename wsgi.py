#!/usr/bin/env python3
"""
WSGI Entry Point for KPCL Automation Application
"""

import os
import sys

# Add the application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, socketio

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
