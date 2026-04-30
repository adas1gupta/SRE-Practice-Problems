from dataclasses import dataclass
from collections import defaultdict
import argparse 
import random
import statistics
import json

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
    machines = []

    for machine_id in range(num_machines):
        machine_rack = random.choice(racks)
        machine_datacenter = random.choice(datacenters)
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
    
    cpu_quartiles = statistics.quantiles(cpu_list, n=4)
    cpu_p25, cpu_p75 = cpu_quartiles[0], cpu_quartiles[2]
    
    mem_quartiles = statistics.quantiles(mem_list, n=4)
    mem_p25, mem_p75 = mem_quartiles[0], mem_quartiles[2]
    
    gpu_quartiles = statistics.quantiles(gpu_list, n=4)
    gpu_p25, gpu_p75 = gpu_quartiles[0], gpu_quartiles[2]
    
    cpu_p95 = statistics.quantiles(cpu_list, n=20)[18]
    mem_p95 = statistics.quantiles(mem_list, n=20)[18]
    gpu_p95 = statistics.quantiles(gpu_list, n=20)[18]

    cpu_tuple = (statistics.mean(cpu_list), cpu_p25, cpu_p75, cpu_p95)
    mem_tuple = (statistics.mean(mem_list), mem_p25, mem_p75, mem_p95)
    gpu_tuple = (statistics.mean(gpu_list), gpu_p25, gpu_p75, gpu_p95)

    return [cpu_tuple, mem_tuple, gpu_tuple]

def is_stranded(machine: Machine) -> bool:
    return machine.cpu_used_pct < 20 and machine.memory_used_pct < 20 and machine.gpu_used_pct < 20

def get_stranded(machines: list[Machine]) -> list[Machine]:
    return [m for m in machines if is_stranded(m)]

def is_hotspot(machine: Machine) -> bool:
    return machine.cpu_used_pct > 85 or machine.memory_used_pct > 85 or machine.gpu_used_pct > 85

def get_hotspots(machines: list[Machine]) -> list[Machine]:
    return [m for m in machines if is_hotspot(m)]

def group_machines_by_rack(machines: list[Machine]) -> dict:
    rack_groups = defaultdict(list)

    for machine in machines:
        rack_groups[machine.rack].append(machine)

    return rack_groups 

def group_machines_by_datacenter(machines: list[Machine]) -> dict: 
    datacenter_groups = defaultdict(list)

    for machine in machines:
        datacenter_groups[machine.datacenter].append(machine)

    return datacenter_groups

def decommission(group_dict: dict) -> list:
    decommission_list = []

    for key, val in group_dict.items():
        util_avg = sum((m.cpu_used_pct + m.gpu_used_pct + m.memory_used_pct) / 3 for m in val) / len(val)
        
        if util_avg < 30: 
            decommission_list.append(key)
    
    return decommission_list

def produce_summary_report():
    machines = orchestrate_machines()
    total_machine_count = len(machines)
    stranded_count = len(get_stranded(machines))
    hotspot_count = len(get_hotspots(machines))
    utilized_count = total_machine_count - stranded_count - hotspot_count

    idle_racks = decommission(group_machines_by_rack(machines))
    idle_datacenters = decommission(group_machines_by_datacenter(machines))
    stats = compute_stats(machines)

    report_dict = {
        "total_machine_count": total_machine_count, 
        "stranded_count": stranded_count,
        "hotspot_count": hotspot_count, 
        "utilized_count": utilized_count, 
        "idle_racks": idle_racks,
        "idle_datacenters": idle_datacenters,
        "stats": stats
    }

    report_json = json.dumps(report_dict)
    print(report_json)

    return report_json

if __name__ == "__main__":
    produce_summary_report()