#!/usr/bin/env python3

import time
from watchdog.observers import Observer
from nswatcher import NSWatcher
import logging
import argparse


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help='Path to a config file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print debug information')
    return parser.parse_args(argv)


def setup_logging(loglevel):
    logging.basicConfig(level=loglevel,
                        format='%(asctime)s - %(name)s - %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')


def main(argv=None):
    args = parse_args(argv)
    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG
    setup_logging(loglevel)
    my_event_handler = NSWatcher(debug=args.verbose)
    observer = Observer()
    observer.schedule(my_event_handler, my_event_handler.watch_folder, recursive=True)
    observer.start()
    logging.info("NS-watcher has started !")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("NS-watcher has stopped, bye !")
    observer.join()


if __name__ == "__main__":
    main()
