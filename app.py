# from npmvisual import create_an_item, create_app
from npmvisual import create_app

# app = create_app()

# create_an_item()
# print("create_an_item() completed")
print("create_app called")
app = create_app()
print("create_app finished")

if False and app.config["DEBUG"]:
    import os
    import time

    import psutil

    # Start memory usage monitoring
    pid = os.getpid()
    process = psutil.Process(pid)

    while True:
        print(f"Memory usage: {process.memory_info().rss / (1024 ** 2):.2f} MB")
        time.sleep(30)
