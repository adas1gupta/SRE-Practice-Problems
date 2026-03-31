import argparse
import os

parser = argparse.ArgumentParser(description="cgroups resource enforcer")
parser.add_argument("--name", required=True, help="Name for the cgroup")
parser.add_argument("--memory-limit", required=True, help="Memory limit for the cgroup", type=int)
parser.add_argument("--cpu-limit", required=True, help="CPU limit for the cgroup")
args = parser.parse_args() # parses into key value pairs, but in a namespace, not a dict (e.g, "name": ?)

cgroup_name = args.name
cgroup_dir = f"/sys/fs/cgroup/{cgroup_name}/" 
os.makedirs(cgroup_dir)

def write_memory_limit(mem_limit: int) -> None:
    with open(cgroup_dir + "memory.max", "w") as f:
        f.write(str(mem_limit))
    
def write_cpu_limit(cpu_limit: str) -> None:
    with open(cgroup_dir + "cpu.max", "w") as f:
        f.write(cpu_limit)

write_memory_limit(args.memory_limit)
write_cpu_limit(args.cpu_limit)