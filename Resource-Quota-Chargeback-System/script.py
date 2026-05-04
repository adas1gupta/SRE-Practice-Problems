from dataclasses import dataclass 
from uuid import uuid4, UUID 
from datetime import datetime
import time 
import threading

CPU_RATE = 0.10   # $ per CPU per month
MEMORY_RATE = 0.01  # $ per GB per month
GPU_RATE = 2.00   # $ per GPU per month

class QuotaExceededError(Exception):
    pass

class InsufficientAllocationError(Exception):
    pass

@dataclass
class Team:
    team_id: UUID
    name: str
    # Hard limits
    max_cpu: int
    max_memory: int 
    max_gpu: int 

    # Reserved Capacity
    allocated_cpu: int = 0
    allocated_memory: int = 0
    allocated_gpu: int = 0

    used_cpu: int = 0
    used_memory: int = 0
    used_gpu: int = 0

    @property
    def cpu_waste(self):
        return self.allocated_cpu - self.used_cpu
    
    @property
    def memory_waste(self):
        return self.allocated_memory - self.used_memory
    
    @property
    def gpu_waste(self):
        return self.allocated_gpu - self.used_gpu
    
    @property
    def is_wasteful(self):
        def wasteful(used, allocated):
            if allocated == 0:
                return False
            return (used / allocated) < 0.6
        
        return wasteful(self.used_cpu, self.allocated_cpu) or \
            wasteful(self.used_memory, self.allocated_memory) or \
            wasteful(self.used_gpu, self.allocated_gpu)

@dataclass
class BorrowRecord:
    borrower: Team
    lender: Team
    resource: str 
    amount: int 
    expiry: datetime

@dataclass 
class TeamReport:
    team_name: str 
    cpu_allocation: int
    memory_allocation: int
    gpu_allocation: int 
    cpu_utilization: int 
    mem_utilization: int 
    gpu_utilization: int
    waste_cpu: int 
    waste_mem: int 
    waste_gpu: int 
    total_cost: int 
    wasteful_flag: bool

class QuotaManager():
    RESOURCE_ATTRS = {
        "cpu": ("allocated_cpu", "max_cpu"),
        "memory": ("allocated_memory", "max_memory"),
        "gpu": ("allocated_gpu", "max_gpu"),
    }

    def __init__(self):
        self.team_registry = {}
        self.borrowed_records = []    
    
    def add_team(self, team: Team):
        if team.name in self.team_registry: return 
        self.team_registry[team.name] = team
    
    def allocate(self, team: Team, resource: str, amount: int) -> None:
        if resource not in self.RESOURCE_ATTRS:
            raise ValueError(f"Unknown resource: {resource}")
        
        allocated_attr, max_attr = self.RESOURCE_ATTRS[resource]
        
        if getattr(team, allocated_attr) + amount > getattr(team, max_attr):
            raise QuotaExceededError(f"Max {resource} exceeded")
        setattr(team, allocated_attr, getattr(team, allocated_attr) + amount)
    
    def release(self, team: Team, resource: str, amount: int) -> None:
        if resource not in self.RESOURCE_ATTRS:
            raise ValueError(f"Unknown resource: {resource}")

        allocated_attr, max_attr = self.RESOURCE_ATTRS[resource]
        
        if getattr(team, allocated_attr) - amount < 0:
            raise InsufficientAllocationError(f"Not enough {resource}")
        setattr(team, allocated_attr, getattr(team, allocated_attr) - amount) 

    def borrow(self, borrower: Team, lender: Team, resource: str, amount: int, timestamp) -> BorrowRecord:
        if resource not in self.RESOURCE_ATTRS:
            raise ValueError(f"Unknown resource: {resource}")
        
        allocated_attr, max_attr = self.RESOURCE_ATTRS[resource]
        
        if getattr(lender, max_attr) - getattr(lender, allocated_attr) < amount:
            raise InsufficientAllocationError(f"Not enough {resource}")
        else:
            setattr(lender, max_attr, getattr(lender, max_attr) - amount) 
            setattr(borrower, max_attr, getattr(borrower, max_attr) + amount) 
            self.allocate(borrower, resource, amount)
            record = BorrowRecord(borrower, lender, resource, amount, timestamp)
            
        self.borrowed_records.append(record)
        return record 
    
    def expire_borrows(self) -> None:
        current_time = datetime.now()
        new_records = []

        for r in self.borrowed_records:
            if r.expiry >= current_time:
                new_records.append(r)
            else:
                _, max_attr = self.RESOURCE_ATTRS[r.resource]
                setattr(r.lender, max_attr, getattr(r.lender, max_attr) + r.amount)
                setattr(r.borrower, max_attr, getattr(r.borrower, max_attr) - r.amount)
                
        self.borrowed_records = new_records
    
    def start_expiry_worker(self, interval) -> None:
        def worker():
            while True:
                time.sleep(interval)
                self.expire_borrows()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def generate_report(self) -> None:
        reports = []
        for team_name, team in self.team_registry.items():
            cpu_util = (team.used_cpu / team.allocated_cpu if team.allocated_cpu > 0 else 0) * 100
            mem_util = (team.used_memory / team.allocated_memory if team.allocated_memory > 0 else 0) * 100
            gpu_util = (team.used_gpu / team.allocated_gpu if team.allocated_gpu > 0 else 0) * 100
            cost = (team.allocated_cpu * CPU_RATE) + (team.allocated_memory * MEMORY_RATE) + (team.allocated_gpu * GPU_RATE)

            report = TeamReport(
                team_name, 
                team.allocated_cpu,
                team.allocated_memory,
                team.allocated_gpu,
                cpu_util,
                mem_util,
                gpu_util,
                100 - cpu_util,
                100 - mem_util, 
                100 - gpu_util,
                cost, 
                team.is_wasteful
            )

            reports.append(report)
        
        return reports

if __name__ == "__main__":
    quota_manager = QuotaManager()

    team_a = Team(team_id=uuid4(), name="infra", max_cpu=100, max_memory=256, max_gpu=8)
    team_b = Team(team_id=uuid4(), name="ml", max_cpu=200, max_memory=512, max_gpu=16)
    team_c = Team(team_id=uuid4(), name="product", max_cpu=50, max_memory=128, max_gpu=4)

    quota_manager.add_team(team_a)
    quota_manager.add_team(team_b)
    quota_manager.add_team(team_c)
    
    quota_manager.allocate(team_a, "cpu", 20)

    team_a.used_gpu = 4
    
     