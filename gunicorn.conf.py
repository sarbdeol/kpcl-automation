#!/usr/bin/env python3
"""
Gunicorn Configuration File
Production settings for KPCL Automation Flask Application
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/root/kpcl-automation/logs/gunicorn_access.log"
errorlog = "/root/kpcl-automation/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "kpcl-automation"

# Server mechanics
daemon = False
pidfile = "/root/kpcl-automation/logs/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in future)
# keyfile = None
# certfile = None

# Worker timeout
graceful_timeout = 30
worker_tmp_dir = "/dev/shm"

# Preload application for better performance
preload_app = True

# Enable worker recycling
max_worker_memory = 200  # MB

# Environment
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/root/kpcl-automation'
]

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")
