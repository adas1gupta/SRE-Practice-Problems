import threading
import queue
import time
import signal

shutdown, reload_config = threading.Event(), False

tasks = queue.Queue()

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

def handler(signum, frame):
    if signum == signal.SIGINT or signum == signal.SIGTERM:
        shutdown.set()

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

while not shutdown.is_set():
    time.sleep(1)

print("\nshutdown received, waiting for workers...")
for t in threads:
    t.join()
print("daemon exited cleanly")
