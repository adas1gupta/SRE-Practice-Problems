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
