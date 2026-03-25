from dataclasses import dataclass 
import time
import os

@dataclass
class ProcessInfo:
    pid: int
    name: str
    state: str 
    cpu_usage: float
    memory_usage_rss: float 
    memory_usage_virtual: float 
    open_fd_count: int 
    thread_count: int    

    def __str__(self):
        return f"{self.pid:<8}{self.name:<20}{self.state:<8}{self.cpu_usage:<10}{self.memory_usage_rss:<12}{self.memory_usage_virtual:<12}{self.open_fd_count:<8}{self.thread_count:<8}"


def list_process_ids():
    return [int(p) for p in os.listdir("/proc/") if p.isnumeric()]

def parse_stat(pid: int) -> dict: 
    fields = {}

    with open(f"/proc/{pid}/stat") as f:
        data = f.read().split(" ")

        fields["pid"] = int(data[0])
        fields["name"] = data[1][1:len(data[1]) - 1]
        fields["state"] = data[2]
        fields["CPU jiffies"] = int(data[13]) + int(data[14])
        fields["thread count"] = int(data[19])
    
    return fields

def parse_status(pid: int) -> dict: 
    fields = {}

    with open(f"/proc/{pid}/status") as f:
        for line in f:
            if "VmRSS" in line:
                fields["VmRSS"] = int(line.split()[1])
            elif "VmSize" in line:
                fields["VmSize"] = int(line.split()[1])

    return fields

def count_open_file_descriptors(pid: int) -> int:    
    return len(os.listdir(f"/proc/{pid}/fd/"))

def compute_cpu_percentage(process_ids: list[int]) -> dict:
    pid_cpu_percentages = {}

    for pid in process_ids:
        first_half = parse_stat(pid)["CPU jiffies"]
        pid_cpu_percentages[pid] = -first_half
    
    time.sleep(1)

    for pid in process_ids:
        second_half = parse_stat(pid)["CPU jiffies"]

        pid_cpu_percentages[pid] += second_half
    
    return pid_cpu_percentages

def get_process_info(pid: int, cpu_percentage: float) -> ProcessInfo:
    stats = parse_stat(pid)
    status = parse_status(pid)
    open_fd_total = count_open_file_descriptors(pid)

    return ProcessInfo(
        pid = stats["pid"],
        name = stats["name"],
        state = stats["state"],
        cpu_usage = cpu_percentage,
        memory_usage_rss = status["VmRSS"], 
        memory_usage_virtual = status["VmSize"],
        open_fd_count = open_fd_total,
        thread_count = stats["thread count"]    
    )

def get_all_processes() -> list[ProcessInfo]:
    process_ids = list_process_ids()
    cpu_percentages = compute_cpu_percentage(process_ids)

    process_info_list = []

    for pid in process_ids:
        try:
            process_info_list.append(get_process_info(pid, cpu_percentages[pid]))
        except FileNotFoundError:
            continue
        except KeyError:
            continue
        except PermissionError:
            continue

    return process_info_list

def display(processes: list[ProcessInfo]):
    print("\033[2J\033[H", end="")

    print("PID    NAME             STATE    CPU%    RSS(KB)    VIRT(KB)    FDs    THREADS")
    processes.sort(key=lambda x: x.cpu_usage, reverse=True)
    for process in processes:
        print(process)
    
if __name__ == "__main__":
    while True:
        display(get_all_processes())
        