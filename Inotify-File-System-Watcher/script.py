import argparse
import inotify_simple

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

    while True: 
        events = inotify.read()

        for event in events: 
            if event.mask & inotify_simple.flags.CREATE:
                print(f"path: {event.path}, event type: {event.event_type}, timestamp: {event.timestamp}")

                if event.mask & inotify_simple.flags.ISDIR:
                    nd = inotify.add_watch(watched_directory, 
                        inotify_simple.flags.CREATE | 
                        inotify_simple.flags.MODIFY | 
                        inotify_simple.flags.DELETE |
                        inotify_simple.flags.MOVED_FROM | 
                        inotify_simple.flags.MOVED_TO | 
                        inotify_simple.flags.ATTRIB)
                    
                else:
                    with open(event.path, 'r') as f:
                        file_contents[event.path] = f.read()

            elif event.mask & inotify_simple.flags.DELETE:
                print(f"path: {event.path}, event type: {event.event_type}, timestamp: {event.timestamp}")
            
            elif event.mask & inotify_simple.flags.MODIFY:
                with open(event.path, 'r') as f:
                    diff = f.read()
                    
                print(f"path: {event.path}, event type: {event.event_type}, timestamp: {event.timestamp}", diff)
                file_contents[event.path] = diff

            elif event.mask & inotify_simple.flags.MOVED_FROM:
                print(f"path: {event.path}, event type: {event.event_type}, timestamp: {event.timestamp}")
                pending_moves[event.cookie] = event.name
            
            elif event.mask & inotify_simple.flags.MOVED_TO:
                print(f"path: {event.path}, event type: {event.event_type}, timestamp: {event.timestamp}")
                file_contents[event.name] = file_contents[pending_moves[event.cookie]]
                del file_contents[pending_moves[event.cookie]]
            
            elif event.mask & inotify_simple.flags.ATTRIB:
                print(f"path: {event.path}, event type: {event.event_type}, timestamp: {event.timestamp}")