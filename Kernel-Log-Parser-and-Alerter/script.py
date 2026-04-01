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

if __name__ == "__main__":
    fd = os.open("/dev/kmsg", os.O_RDONLY | os.O_NONBLOCK)

    with open(fd, "r") as f:
        while not shutdown.is_set():
            try:
                print(f.readline(), end="")
            except BlockingIOError:
                time.sleep(0.1)