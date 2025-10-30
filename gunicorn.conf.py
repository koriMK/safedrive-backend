import os

bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
workers = 1
worker_class = "sync"
timeout = 30
preload_app = True
max_requests = 1000
max_requests_jitter = 50