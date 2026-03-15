import threading
import queue
import time
import signal
import json

shutdown, reload_config, active_tasks = threading.Event(), threading.Event(), threading.Event()

tasks = queue.Queue()

def read_config():
    with open("config.json", "r") as f:
        return json.load(f)

def do_work(task):
    print(f"doing work: {task}")
    time.sleep(0.5)  # simulate work

def worker():
    while not shutdown.is_set():
        try:
            task = tasks.get(timeout=1.0)
            do_work(task)
        except queue.Empty:
            continue

threads = [threading.Thread(target=worker) for _ in range(3)]
for t in threads:
    t.start()


# can't do anything else besides setting variables here because signal handlers are called by the OS and can interrupt a program at any point.
# As a result, you should only do things that are atomic and cannot be corrupted by interruption. 
# Such as "Setting Flags" or "Writing to a File Descriptor with write()"
def handler(signum, frame):
    if signum == signal.SIGINT or signum == signal.SIGTERM:
        shutdown.set()
    elif signum == signal.SIGHUP:
        reload_config.set()
    elif 
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGUSR1, handler)

config = read_config()

# Everything else goes in the main loop
while not shutdown.is_set():
    if reload_config.is_set():
        config = read_config()
        print(f"config reloaded: {config}")
        reload_config.clear()
    time.sleep(1)

print("\nshutdown received, waiting for workers...")
for t in threads:
    t.join()
print("daemon exited cleanly")
