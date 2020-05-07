import multiprocessing

bind = '127.0.0.1:5001'
workers = multiprocessing.cpu_count()* 2 + 1
worker_class = 'gevent'
worker_connections = 1000
