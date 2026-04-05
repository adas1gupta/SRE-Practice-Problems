from dataclasses import dataclass 


@dataclass
class Machine:
    machine_id: int
    total_cpu: int
    total_memory: int
    total_gpu: int

    allocated_cpu: int = 0
    allocated_memory: int = 0
    allocated_gpu: int = 0

    @property
    def available_cpu(self):
        return self.total_cpu - self.allocated_cpu
    
    @property
    def available_memory(self):
        return self.total_memory - self.allocated_memory
    
    @property
    def available_gpu(self):
        return self.total_gpu - self.allocated_gpu
    

@dataclass
class Job:
    job_id: int
    required_cpu: int
    required_memory: int 
    required_gpu: int 
    priority: int

def fits(job: Job, machine: Machine) -> bool:
    return job.required_cpu <= machine.available_cpu and job.required_memory <= machine.available_memory and job.required_gpu <= machine.available_gpu

def place_job(job: Job, machine: Machine) -> None:
    machine.allocated_cpu += job.required_cpu
    machine.allocated_gpu += job.required_gpu 
    machine.allocated_memory += job.required_memory

def first_fit_decreasing(jobs: list[Job], machines: list[Machine]) -> list[Job]:
    unplaced_jobs = []
    sorted_jobs = sorted(jobs, key=lambda x: x.required_cpu + x.required_gpu + x.required_memory, reverse=True)
    for job in sorted_jobs:
        placed = False 
        for machine in machines:
            if fits(job, machine):
                place_job(job, machine)
                placed = True
                break
        
        if not placed:
            unplaced_jobs.append(job)
    
    return unplaced_jobs

def best_fit(jobs: list[Job], machines: list[Machine]) -> list[Job]:
    unplaced_jobs = []
    sorted_jobs = sorted(jobs, key=lambda x: x.required_cpu + x.required_gpu + x.required_memory, reverse=True)
    
    for job in sorted_jobs:
        placed_machines = []

        for machine in machines:
            if fits(job, machine):
                cpu_scalar = machine.available_cpu / machine.total_cpu
                gpu_scalar = machine.available_gpu / machine.total_gpu
                memory_scalar = machine.available_memory / machine.total_memory
                total_scalar = cpu_scalar + gpu_scalar + memory_scalar

                placed_machines.append((machine, total_scalar))

        if len(placed_machines) == 0:
            unplaced_jobs.append(job)
        else:
            placed_machines.sort(key=lambda x: x[1])
            place_job(job, placed_machines[0][0])
            
    
    return unplaced_jobs