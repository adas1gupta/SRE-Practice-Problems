from dataclasses import dataclass
import argparse 
import random
import statistics

parser = argparse.ArgumentParser(description="Fleet Utilization Tracker")
parser.add_argument("--machines", help="number of machines to dispatch", default=100, type=int)
args = parser.parse_args()

@dataclass 
class Machine:
    machine_id: int 
    rack: str 
    datacenter: str 
    cpu_used_pct: float 
    memory_used_pct: float 
    gpu_used_pct: float 

racks = ["rack-1", "rack-2", "rack-3", "rack-4", "rack-5"]
datacenters = ["dc-east", "dc-west", "dc-central"]

def orchestrate_machines() -> list[Machine]:
    num_machines = args.machines
    num_racks = len(racks)
    num_datacenters = len(datacenters)
    machines = []

    for machine_id in range(num_machines):
        machine_rack = random.choice(racks)
        machine_datacenter = random.choice(num_datacenters)
        cpu_used = random.uniform(0, 100)
        memory_used = random.uniform(0, 100)
        gpu_used = random.uniform(0, 100)
        
        machine = Machine(
            machine_id,
            machine_rack,
            machine_datacenter,
            cpu_used,
            memory_used,
            gpu_used
        )

        machines.append(machine)
    
    return machines

def compute_stats(machines: list[Machine]) -> list[tuple]:
    cpu_list = [machine.cpu_used_pct for machine in machines]
    mem_list = [machine.memory_used_pct for machine in machines]
    gpu_list = [machine.gpu_used_pct for machine in machines]
    
    cpu_quartiles = statistics.quantiles(cpu_list, 4)
    cpu_p25, cpu_p75 = cpu_quartiles[0], cpu_quartiles[2]
    
    mem_quartiles = statistics.quantiles(mem_list, 4)
    mem_p25, mem_p75 = mem_quartiles[0], mem_quartiles[2]
    
    gpu_quartiles = statistics.quantiles(gpu_list, 4)
    gpu_p25, gpu_p75 = gpu_quartiles[0], gpu_quartiles[2]
    
    cpu_p95 = statistics.quantiles(cpu_list, 20)[18]
    mem_p95 = statistics.quantiles(mem_list, 20)[18]
    gpu_p95 = statistics.quantiles(gpu_list, 20)[18]

    cpu_tuple = (statistics.mean(cpu_list), cpu_p25, cpu_p75, cpu_p95)
    mem_tuple = (statistics.mean(mem_list), mem_p25, mem_p75, mem_p95)
    gpu_tuple = (statistics.mean(gpu_list), gpu_p25, gpu_p75, gpu_p95)

    return [cpu_tuple, mem_tuple, gpu_tuple]