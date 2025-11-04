# Gunicorn configuration for Artemis API
import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = 'sync'
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '/var/log/gunicorn/access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '/var/log/gunicorn/error.log')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'artemis-api'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
ssl_version = 5
cert_reqs = 0
ca_certs = None
suppress_ragged_eof = True

# Application
preload_app = False
