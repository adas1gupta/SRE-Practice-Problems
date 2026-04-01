import threading 
import signal
import os
import time

shutdown = threading.Event()

def signal_handler(signum, frame):
    if signum == signal.SIGINT or signum == signal.SIGTERM:
        shutdown.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_raw_line(line: str) -> dict:
    if line.startswith(" "):
        return {"continuation": True, "message": line.strip()}

    halves = line.split(";")
    left_half = halves[0].split(",")
    priority, sequence, timestamp, flags = left_half

    return {
        "priority": int(priority),
        "sequence": int(sequence),
        "timestamp": int(timestamp),
        "flags": flags,
        "message": halves[1].strip(),
        "continuation": False
    }

if __name__ == "__main__":
    fd = os.open("/dev/kmsg", os.O_RDONLY | os.O_NONBLOCK)

    with open(fd, "r") as f:
        while not shutdown.is_set():
            try:
                print(f.readline(), end="")
            except BlockingIOError:
                time.sleep(0.1)