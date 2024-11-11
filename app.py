from npmvisual import create_app

app = create_app()

if app.config["DEBUG"]:
    import os
    import time

    import psutil

    # Start memory usage monitoring
    pid = os.getpid()
    process = psutil.Process(pid)

    while True:
        print(f"Memory usage: {process.memory_info().rss / (1024 ** 2):.2f} MB")
        time.sleep(30)
