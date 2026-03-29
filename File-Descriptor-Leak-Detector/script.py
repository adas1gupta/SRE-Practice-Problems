import signal
import threading
import time
import os
import json

shutdown = threading.Event()
tracking_history = {}
N = int(os.getenv("SAMPLES",  5))

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

def track_history(pid: int, name: str, fd_count: int) -> None:
    identifier = (pid, name)
        
    if identifier not in tracking_history: 
        tracking_history[identifier] = []
        
    tracking_history[identifier].append(fd_count)
    tracking_history[identifier] = tracking_history[identifier][-N:]

def detect_growth(identifier: tuple[int, str]) -> bool:
    counter = 0
    most_recent = None 

    try:
        for count in tracking_history[identifier]:
            if most_recent is not None and count > most_recent:
                counter += 1
            else:
                counter = 0

            most_recent = count 

            if counter >= N: return True

    except KeyError:
        return False

## every entry in /proc/<pid>/fd/ is a symlink, not a file
def categorize_fd_count(pid: int) -> dict | None:
    categorized_fd = {
        "file": 0,
        "socket": 0,
        "pipe": 0, 
        "character device": 0
    }

    try:
        for item in os.listdir(f"/proc/{pid}/fd"): 
            try:
                fd_type = os.readlink(f"/proc/{pid}/fd/{item}")
            except FileNotFoundError:
                continue 

            if "socket:" in fd_type: 
                categorized_fd["socket"] += 1
            elif "pipe:" in fd_type: 
                categorized_fd["pipe"] += 1
            elif "/dev/" in fd_type: 
                categorized_fd["character device"] += 1
            else:
                categorized_fd["file"] += 1

        return categorized_fd
    except (PermissionError, FileNotFoundError): 
        return None

def get_top_file_paths(pid: int) -> list[str] | None:
    try:
        file_path_freq = Counter()
        
        for item in os.listdir(f"/proc/{pid}/fd"): 
            try:
                fd_type = os.readlink(f"/proc/{pid}/fd/{item}")

                if fd_type.startswith("/"):
                    file_path_freq[fd_type] += 1

            except FileNotFoundError:
                continue 
        
        return file_path_freq.most_common(10)
        
    except (PermissionError, FileNotFoundError): 
        return None


def generate_alert(pid: int, name: str) -> None:
    fd_list = tracking_history[(pid, name)]
    
    message_dict = {
        "pid": pid,
        "name": name, 
        "fd count": fd_list[-1],
        "growth rate": 0, 
        "categories": categorize_fd_count(pid),
        "top paths": get_top_file_paths(pid) 
    }
    
    if len(fd_list) < N and len(fd_list) >= 2: 
        message_dict["growth rate"] = (fd_list[-1] - fd_list[0]) / (len(fd_list) - 1)
    else:
        message_dict["growth rate"] = (fd_list[-1] - fd_list[-N]) / (N - 1)
    
    print(json.dumps(message_dict))

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

if __name__ == "__main__":
    while not shutdown.is_set():
        processes_list = collect_all_processes()

        for pid, name, fd_count in processes_list:
            track_history(pid, name, fd_count)

            if detect_growth((pid, name)):
                generate_alert(pid, name)

        time.sleep(30)