import threading
import queue
import time
import signal
import json

shutdown, reload_config, dump_state = threading.Event(), threading.Event(), threading.Event()
active_tasks = 0
start_time = time.time()
active_tasks_lock = threading.Lock()

tasks = queue.Queue()

def read_config():
    with open("config.json", "r") as f:
        return json.load(f)

def do_work(task):
    print(f"doing work: {task}")
    time.sleep(0.5)  # simulate work

def worker():
    global active_tasks
    while not shutdown.is_set():
        try:
            task = tasks.get(timeout=1.0)

            with active_tasks_lock:
                active_tasks += 1
            
            do_work(task)
            
            with active_tasks_lock:
                active_tasks -= 1
        
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
    elif signum == signal.SIGUSR1:
        dump_state.set()

def write_to_log_file(payload):
    with open("logs.txt", 'w') as f:
        f.write(json.dumps(payload, indent=2))

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

    if dump_state.is_set():
        dump_payload = {"queue_depth": tasks.qsize(), "uptime": time.time() - start_time, "active_tasks": active_tasks}
        write_to_log_file(dump_payload)
        dump_state.clear()
    
    time.sleep(1)

print("\nshutdown received, waiting for workers...")
for t in threads:
    t.join()
print("daemon exited cleanly")
