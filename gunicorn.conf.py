import os

bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
workers = 1
worker_class = "sync"
timeout = 120
keepalive = 5
preload_app = True
max_requests = 500
max_requests_jitter = 25
worker_tmp_dir = "/dev/shm"
worker_connections = 1000
graceful_timeout = 30
max_worker_memory = 200