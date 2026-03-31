import argparse
import os
import subprocess
import signal
import threading

parser = argparse.ArgumentParser(description="cgroups resource enforcer")
parser.add_argument("--name", required=True, help="Name for the cgroup")
parser.add_argument("--memory-limit", required=True, help="Memory limit for the cgroup", type=int)
parser.add_argument("--cpu-limit", required=True, help="CPU limit for the cgroup")
parser.add_argument("--cmd", required=True, help="Command for the child process")
args = parser.parse_args() # parses into key value pairs, but in a namespace, not a dict (e.g, "name": ?)
shutdown = threading.Event()

cgroup_name = args.name
cgroup_dir = f"/sys/fs/cgroup/{cgroup_name}/" 
os.makedirs(cgroup_dir)

def write_memory_limit(mem_limit: int) -> None:
    with open(cgroup_dir + "memory.max", "w") as f:
        f.write(str(mem_limit))
    
def write_cpu_limit(cpu_limit: str) -> None:
    with open(cgroup_dir + "cpu.max", "w") as f:
        f.write(cpu_limit)

def launch_child_process(command: list[str]) -> subprocess.Popen:
    return subprocess.Popen(command)

def add_to_cgroup(pid: int) -> None:
    with open(cgroup_dir + "cgroup.procs", "w") as f:
        f.write(str(pid))

def signal_handler(signum, frame):
    if signum == signal.SIGINT or signum == signal.SIGTERM:
        shutdown.set()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

write_memory_limit(args.memory_limit)
write_cpu_limit(args.cpu_limit)
child_proc = launch_child_process(args.cmd.split())
add_to_cgroup(child_proc.pid)

if __name__ == "__main__":
    while not shutdown.is_set():
        pass