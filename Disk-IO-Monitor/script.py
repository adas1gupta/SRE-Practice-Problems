import time 

def parse_diskstats(filepath: str) -> dict:
    device_dict = {}

    with open(filepath, 'r') as f:    
        for line in f:
            _, _, device_name, reads_done, _, sectors_read, read_time, writes_done, _, sectors_written, write_time, _, iotime, _ = line.split() 
            device_dict[device_name] = {
                "reads done": int(reads_done), 
                "writes done": int(writes_done),
                "read time": int(read_time),
                "write time": int(write_time),
                "sectors read": int(sectors_read), 
                "sectors written": int(sectors_written), 
                "time in io": int(iotime),  
            }
    
    return device_dict

def compute_disk_metrics(first_snapshot: dict, second_snapshot: dict, elapsed_time: int) -> dict: 
    metrics = {}

    for device in second_snapshot.keys():
        if device in first_snapshot:
            s1 = first_snapshot[device]
            s2 = second_snapshot[device]

            delta_reads = s2["reads done"] - s1["reads done"]
            delta_writes = s2["writes done"] - s1["writes done"]
            delta_sectors_read = s2["sectors read"] - s1["sectors read"]
            delta_sectors_written = s2["sectors written"] - s1["sectors written"]
            delta_time_in_io = s2["time in io"] - s1["time in io"]
            total_ios = delta_reads + delta_writes

            metrics[device] = {
                "reads_per_sec": delta_reads / elapsed_time,
                "writes_per_sec": delta_writes / elapsed_time,
                "read_mb_per_sec": ((delta_sectors_read * 512) / (1024 * 1024)) / elapsed_time,
                "write_mb_per_sec": ((delta_sectors_written * 512) / (1024 * 1024)) / elapsed_time,
                "util_pct": (delta_time_in_io / (elapsed_time * 1000)) * 100,
                "avg_latency_ms": delta_time_in_io / total_ios if total_ios > 0 else 0,
            }

    return metrics

def display_table_metrics(stats: dict) -> None:
    print("Device   Reads/s   Writes/s   Read MB/s   Write MB/s   Util%   Avg Latency(ms)")
    
    for device in stats.keys():
        rps = stats[device]["reads_per_sec"]
        wps = stats[device]["writes_per_sec"]
        rmbps = stats[device]["read_mb_per_sec"]
        wmbps = stats[device]["write_mb_per_sec"]
        util = stats[device]["util_pct"]
        avg_latency = stats[device]["avg_latency_ms"]
        print(f"{device} {rps} {wps} {rmbps} {wmbps} {util} {avg_latency}")

def parse_process_io() -> dict:
    pids = [x for x in os.listdir("/proc") if x.isnumeric()]
    pid_dict = {}

    for pid in pids:
        try:
            with open(f"/proc/{pid}/io", 'r') as f:
                pid_dict[pid] = {}    
                for line in f:
                    key, val = line.split(": ") 
                    val = val.strip()

                    if "read_bytes" in line: 
                        pid_dict[pid]["read_bytes"] = int(val)
                    elif "cancelled_write_bytes" in line:
                        pid_dict[pid]["cancelled_write_bytes"] = int(val)
                    elif "write_bytes" in line:
                        pid_dict[pid]["write_bytes"] = int(val)
                    

        except (FileNotFoundError, PermissionError):
            continue 

    return pid_dict

def compute_process_metrics(first_snapshot: dict, second_snapshot: dict, elapsed_time: int) -> dict: 
    metrics = {}

    for pid in second_snapshot.keys():
        if pid in first_snapshot:
            s1 = first_snapshot[pid]
            s2 = second_snapshot[pid]

            delta_reads = s2["read_bytes"] - s1["read_bytes"]
            delta_writes = s2["write_bytes"] - s1["write_bytes"]
            read_mbps = (delta_reads / (1024 * 1024)) / elapsed_time
            write_mbps = ((delta_writes - cancelled_write_bytes) / (1024 * 1024)) / elapsed_time
            total_throughput = read_mbps + write_mbps

            metrics[pid] = {
                "read_mb_per_sec": read_mbps,
                "write_mb_per_sec": write_mbps,
                "total throughput": total_throughput
            }

    return metrics

def display_process_table(stats: dict) -> None:
    print("Device   Reads/s   Writes/s   Read MB/s   Write MB/s   Util%   Avg Latency(ms)")
    
    for pid in stats.keys():
        rps = stats[pid]["read_mb_per_sec"]
        wps = stats[pid]["write_mb_per_sec"]
        rmbps = stats[device]["read_mb_per_sec"]
        wmbps = stats[device]["write_mb_per_sec"]
        util = stats[device]["util_pct"]
        avg_latency = stats[device]["avg_latency_ms"]
        print(f"{device} {rps} {wps} {rmbps} {wmbps} {util} {avg_latency}")


if __name__ == "__main__":
    diskstats = f"/proc/diskstats"

    t1 = time.perf_counter()
    first_half = parse_diskstats(diskstats)
    time.sleep(2)
    second_half = parse_diskstats(diskstats)
    t2 = time.perf_counter()

    elapsed = t2 - t1 

    diskstats_delta = compute_disk_metrics(first_half, second_half, elapsed)
    display_table_metrics(diskstats_delta)

    process_t1 = time.perf_counter()
    process_first_half = parse_process_io()
    time.sleep(2)
    process_second_half = parse_process_io()
    process_t2 = time.perf_counter()

    process_elapsed = process_t2 - process_t1

    process_stats_delta = compute_process_metrics(process_first_half, process_second_half, process_elapsed)