from dataclasses import dataclass
import argparse 
import random

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
