import signal
import threading
import time
import os

shutdown = threading.Event()

def handler(signum, frame):
    if signum == signal.SIGTERM or signum == signal.SIGINT:
        shutdown.set()

def get_pids() -> list[int]:
    return [int(pid) for pid in os.listdir("/proc") if pid.isnumeric()]

def get_fd_count(pid: int) -> int | None: 
    try: 
        return len(os.listdir(f"/proc/{pid}/fd"))
    except (PermissionError, FileNotFoundError): 
        return None

def get_process_name(pid: int) -> str | None: 
    try: 
        with open(f"/proc/{pid}/comm", "r") as f:
            return f.read().strip()
    except (PermissionError, FileNotFoundError): 
        return None

def collect_all_processes() -> list[tuple]:
    pids = get_pids()
    process_tuples = []

    for pid in pids: 
        fd_count = get_fd_count(pid)
        name = get_process_name(pid)

        if name is None or fd_count is None: continue

        process_tuples.append((pid, name, fd_count))
    
    return process_tuples

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

if __name__ == "__main__":
    while not shutdown.is_set():
        time.sleep(30)