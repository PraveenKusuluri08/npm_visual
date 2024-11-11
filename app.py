import os
import time

import psutil

from npmvisual import create_app

app = create_app()

pid = os.getpid()
process = psutil.Process(pid)

while True:
    print(f"Memory usage: {process.memory_info().rss / (1024 ** 2):.2f} MB")
    time.sleep(30)
