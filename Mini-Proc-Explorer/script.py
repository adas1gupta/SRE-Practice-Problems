from dataclasses import dataclass 

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


def list_process_ids():
    return [int(p) for p in os.listdir("/proc/") if p.isnumeric()]


def parse_stat(pid: int) -> dict: 
    fields = {}

    with open(f"/proc/{pid}/stat") as f:
        data = f.read().split(" ")

        fields["pid"] = data[0]
        fields["name"] = data[1][1:len(data[1]) - 1]
        fields["state"] = data[2]
        fields["CPU jiffies"] = int(data[13]) + int(data[14])
        fields["thread count"] = int(data[19])
    
    return fields

def parse_status(pid: int) -> dict: 
    fields = {}

    with open(f"/proc/{pid}/stat") as f:
        data = f.read().split(" ")

        fields["pid"] = data[0]
        fields["name"] = data[1][1:len(data[1]) - 1]
        fields["state"] = data[2]
        fields["CPU jiffies"] = int(data[13]) + int(data[14])
        fields["thread count"] = int(data[19])
    
    return fields