#!/usr/bin/env python3

import time
from watchdog.observers import Observer
from NSWatcher import NSWatcher
import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s - %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')


def main():
    setup_logging()
    my_event_handler = NSWatcher()
    observer = Observer()
    observer.schedule(my_event_handler, my_event_handler.watch_folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()