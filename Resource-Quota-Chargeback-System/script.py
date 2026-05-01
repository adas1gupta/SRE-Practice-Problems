from dataclasses import dataclass 
from uuid import uuid4, UUID 

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

class QuotaManager():
    def __init__(self):
        self.team_registry = {}
    
    def add_team(self, team: Team):
        if team in self.team_registry: return 
        self.team_registry[team.name] = team
    
    def allocate(self, team: Team, resource: str, amount: int) -> None:
        match resource:
            case "cpu":
                if team.allocated_cpu + amount > team.max_cpu: 
                    raise QuotaExceededError("Max Amount Exceeded")
                else:
                    team.allocated_cpu += amount 
            case "memory":
                if team.allocated_memory + amount > team.max_memory: 
                    raise QuotaExceededError("Max Amount Exceeded")
                else:
                    team.allocated_memory += amount 
            case "gpu":
                if team.allocated_gpu + amount > team.max_gpu: 
                    raise QuotaExceededError("Max Amount Exceeded")
                else:
                    team.allocated_gpu += amount 
    
    def release(self, team: Team, resource: str, amount: int) -> None:
        match resource:
            case "cpu":
                if team.allocated_cpu - amount < 0: 
                    raise InsufficientAllocationError("Not enough CPU")
                else:
                    team.allocated_cpu -= amount 
            case "memory":
                if team.allocated_memory - amount < 0: 
                    raise InsufficientAllocationError("Not enough memory")
                else:
                    team.allocated_memory -= amount 
            case "gpu":
                if team.allocated_gpu - amount < 0: 
                    raise InsufficientAllocationError("Not enough GPU")
                else:
                    team.allocated_gpu -= amount 