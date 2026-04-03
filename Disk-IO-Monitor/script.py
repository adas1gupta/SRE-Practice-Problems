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

if __name__ == "__main__":
    diskstats = f"/proc/diskstats"

    first_half = parse_diskstats(diskstats)
    time.sleep(1)
    second_half = parse_diskstats(diskstats)