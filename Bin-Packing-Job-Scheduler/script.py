from dataclasses import dataclass 
import structlog
import random
import copy

logger = structlog.get_logger()

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
                gpu_scalar = machine.available_gpu / machine.total_gpu if machine.total_gpu > 0 else 0
                memory_scalar = machine.available_memory / machine.total_memory
                total_scalar = cpu_scalar + gpu_scalar + memory_scalar

                placed_machines.append((machine, total_scalar))

        if len(placed_machines) == 0:
            unplaced_jobs.append(job)
        else:
            placed_machines.sort(key=lambda x: x[1])
            place_job(job, placed_machines[0][0])
            
    
    return unplaced_jobs

def generate_machines(amount: int) -> list[Machine]:
    thinking_machines = []

    for m_id in range(amount):
        machine_id = m_id
        total_cpu = random.randint(16, 128)
        total_memory = random.randint(32, 256)
        total_gpu = random.randint(0, 8)

        allocated_cpu = 0
        allocated_memory = 0
        allocated_gpu = 0

        machine = Machine(
            machine_id,
            total_cpu, 
            total_memory,
            total_gpu,
            allocated_cpu,
            allocated_memory, 
            allocated_gpu
        )

        thinking_machines.append(machine)
    
    return thinking_machines

def generate_jobs(amount: int) -> list[Job]:
    jobs = []

    for j_id in range(amount):
        job_id = j_id
        required_cpu = random.randint(16, 128)
        required_memory = random.randint(32, 256)
        required_gpu = random.randint(0, 8)
        priority = random.randint(-19, 20)

        job = Job(
            job_id,
            required_cpu,
            required_memory,
            required_gpu,
            priority
        )

        jobs.append(job)
    
    return jobs

def machine_utilization(machines: list[Machine]) -> float:
    num_machines = len(machines)
    capacities = []
    
    for machine in machines:
        cpu_scalar = machine.allocated_cpu / machine.total_cpu
        gpu_scalar = machine.allocated_gpu / machine.total_gpu if machine.total_gpu > 0 else 0
        memory_scalar = machine.allocated_memory / machine.total_memory
        total_scalar = cpu_scalar + gpu_scalar + memory_scalar

        capacities.append(total_scalar / 3)

    average = sum(capacities)
    return average / num_machines if num_machines > 0 else 0

def machine_fragmentation(unplaced_jobs: list[Job], machines: list[Machine]) -> int:
    placeable_jobs = len(unplaced_jobs)

    for job in unplaced_jobs:
        for machine in machines:
            if fits(job, machine):
                placeable_jobs -= 1
                break
    
    return placeable_jobs

if __name__ == "__main__":
    ffd_machines = generate_machines(10)
    ffd_jobs = generate_jobs(20)

    best_fit_machines = copy.deepcopy(ffd_machines)
    best_fit_jobs = copy.deepcopy(ffd_jobs)

    unplaced_ffd = first_fit_decreasing(ffd_jobs, ffd_machines)
    unplaced_best_fit = best_fit(best_fit_jobs, best_fit_machines)

    ffd_utilization = machine_utilization(ffd_machines)
    best_fit_utilization = machine_utilization(best_fit_machines)

    placeable_ffd = machine_fragmentation(unplaced_ffd, ffd_machines)
    placeable_best_fit = machine_fragmentation(unplaced_best_fit, best_fit_machines)

    logger.info("ffd_results", utilization=ffd_utilization, unscheduled=len(unplaced_ffd), fragmentation=placeable_ffd)
    logger.info("best_fit_results", utilization=best_fit_utilization, unscheduled=len(unplaced_best_fit), fragmentation=placeable_best_fit)