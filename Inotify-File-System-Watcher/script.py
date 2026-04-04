import argparse
import inotify_simple
import threading 
import signal 
import difflib
import os
import json 
from datetime import datetime 

shutdown = threading.Event()

def signal_handler(signum: int, frame) -> None:
    if signum in (signal.SIGINT, signal.SIGTERM):
        shutdown.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Directory to watch")
    parser.add_argument("--directory", required=True, help="directory for Inotify to monitor")

    args = parser.parse_args()
    watched_directory = args.directory

    inotify = inotify_simple.INotify()
    wd = inotify.add_watch(watched_directory, 
                        inotify_simple.flags.CREATE | 
                        inotify_simple.flags.MODIFY | 
                        inotify_simple.flags.DELETE |
                        inotify_simple.flags.MOVED_FROM | 
                        inotify_simple.flags.MOVED_TO | 
                        inotify_simple.flags.ATTRIB)

    descriptor_table = {
        wd: watched_directory
    }

    file_contents = {}
    pending_moves = {}

    while not shutdown.is_set(): 
        events = inotify.read()

        for event in events:
            path = os.path.join(descriptor_table[event.wd], event.name)
            timestamp = datetime.now().isoformat() 
            if event.mask & inotify_simple.flags.CREATE:
                print(json.dumps({
                    "path": path, 
                    "event_type": "CREATE", 
                    "timestamp": timestamp
                }))

                if event.mask & inotify_simple.flags.ISDIR:
                    nd = inotify.add_watch(path, 
                        inotify_simple.flags.CREATE | 
                        inotify_simple.flags.MODIFY | 
                        inotify_simple.flags.DELETE |
                        inotify_simple.flags.MOVED_FROM | 
                        inotify_simple.flags.MOVED_TO | 
                        inotify_simple.flags.ATTRIB)

                    descriptor_table[nd] = path
                else:
                    with open(path, 'r') as f:
                        file_contents[path] = f.read()

            elif event.mask & inotify_simple.flags.DELETE:
                print(json.dumps({
                    "path": path, 
                    "event_type": "DELETE", 
                    "timestamp": timestamp
                }))
            
            elif event.mask & inotify_simple.flags.MODIFY:
                with open(path, 'r') as f:
                    new = f.read()
                
                old_lines = file_contents[path].splitlines(keepends=True)
                new_lines = new.splitlines(keepends=True)
                diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="old", tofile="new"))

                print(json.dumps({
                    "path": path, 
                    "event_type": "MODIFY", 
                    "timestamp": timestamp,
                    "diff": diff

                }))
                
                file_contents[path] = new

            elif event.mask & inotify_simple.flags.MOVED_FROM:
                print(json.dumps({
                    "path": path, 
                    "event_type": "MOVED_FROM", 
                    "timestamp": timestamp
                }))
                pending_moves[event.cookie] = path
            
            elif event.mask & inotify_simple.flags.MOVED_TO:
                print(json.dumps({
                    "path": path, 
                    "event_type": "MOVED_TO", 
                    "timestamp": timestamp
                }))
                file_contents[path] = file_contents[pending_moves[event.cookie]]
                del file_contents[pending_moves[event.cookie]]
                del pending_moves[event.cookie]
            
            elif event.mask & inotify_simple.flags.ATTRIB:
                print(json.dumps({
                    "path": path, 
                    "event_type": "ATTRIB", 
                    "timestamp": timestamp
                }))