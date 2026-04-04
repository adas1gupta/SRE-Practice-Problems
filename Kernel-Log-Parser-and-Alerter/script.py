import threading 
import signal
import os
import time
import re
import json
from enum import Enum

class Category(Enum):
    NORMAL = 0
    OOM = 1
    MACHINE_CHECK_EXCEPTION = 4
    HARDWARE_ERROR = 5
    EDAC = 6
    DISK_ERROR = 7
    FILE_SYSTEM_SPECIFIC = 8
    BLOCK_LAYER_FAILURE = 9
    IO_ERROR = 10
    NIC_HUNG_QUEUE = 11
    LINK_STATE_ISSUES = 12
    CONNTRACK_TABLE_EXHAUSTED = 13

class ParserMode(Enum):
    NORMAL = 0
    OOM_ACCUMULATION = 1

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

def parse_oom_event(line: dict) -> dict:
    match = re.search(r"Killed process (\d+) \((\w+)\) total-vm:(\d+)kB, anon-rss:(\d+)kB", line["message"])
    pid = match.group(1)
    name = match.group(2)
    total_vm = match.group(3)
    anon_rss = match.group(4)

    return {
        "pid": pid, 
        "process_name": name, 
        "total-vm": total_vm, 
        "anon-rss": anon_rss
    }

def classification(parsed: dict) -> Category: 
    message = parsed["message"]

    if re.search(r"oom-killer", message): return Category.OOM
    if re.search(r"Out of memory", message): return Category.OOM
    if re.search(r"Killed process", message): return Category.OOM

    # Hardware
    if re.search(r"MCE", message): return Category.MACHINE_CHECK_EXCEPTION
    if re.search(r"Hardware Error", message): return Category.HARDWARE_ERROR
    if re.search(r"EDAC", message): return Category.EDAC
    if re.search(r"ata|sd", message): return Category.DISK_ERROR

    # Filesystem 
    if re.search(r"EXT4-fs error|XFS.*error|BTRFS.*error", message): return Category.FILE_SYSTEM_SPECIFIC
    if re.search(r"Buffer I/O error", message): return Category.BLOCK_LAYER_FAILURE
    if re.search(r"I/O error, dev", message): return Category.IO_ERROR

    # Network
    if re.search(r"NETDEV WATCHDOG", message): return Category.NIC_HUNG_QUEUE
    if re.search(r"Link is Down", message): return Category.LINK_STATE_ISSUES
    if re.search(r"nf_conntrack: table full", message): return Category.CONNTRACK_TABLE_EXHAUSTED

    return Category.NORMAL


if __name__ == "__main__":
    mode = ParserMode.NORMAL
    oom_lines = []
    
    fd = os.open("/dev/kmsg", os.O_RDONLY | os.O_NONBLOCK)

    with open(fd, "r") as f:
        while not shutdown.is_set():
            try:
                line = f.readline()
                parsed_line = parse_raw_line(line)

                if parsed_line["continuation"]:
                    continue

                if mode == ParserMode.NORMAL:
                    category = classification(parsed_line)
                    if category == Category.OOM:
                        mode = ParserMode.OOM_ACCUMULATION
                        oom_lines.append(parsed_line)
                    else:
                        print(json.dumps({"category": category.name, "message": parsed_line["message"], "timestamp": parsed_line["timestamp"], "severity": parsed_line["priority"] & 0x07}))

                elif mode == ParserMode.OOM_ACCUMULATION:
                    oom_lines.append(parsed_line)
                    if re.search(r"Killed process", parsed_line["message"]):        
                        parsed_oom = parse_oom_event(parsed_line)
                        print(json.dumps({"category": Category.OOM.name, "message": parsed_line["message"], "timestamp": parsed_line["timestamp"], "pid": parsed_oom["pid"], "process_name": parsed_oom["process_name"], "total-vm": parsed_oom["total-vm"], "anon-rss": parsed_oom["anon-rss"], "severity": parsed_line["priority"] & 0x07}))
                        mode = ParserMode.NORMAL
                        oom_lines = []

            except BlockingIOError:
                time.sleep(0.1)