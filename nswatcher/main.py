#!/usr/bin/env python3

from pathlib import Path
import time
import logging
import argparse
from watchdog.observers import Observer
from .watcher import NSWatcher
from .watcher import DEFAULT_CFG_PATH


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help='Path to a config file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print debug information')
    return parser.parse_args(argv)


def get_config(given_cfg_path):
    if given_cfg_path is not None and Path(given_cfg_path).is_file():
        logging.debug(f"Given config file {given_cfg_path} detected")
        return given_cfg_path
    elif Path(DEFAULT_CFG_PATH).is_file():
        logging.debug(f"Default config file {DEFAULT_CFG_PATH} will be used")
        return DEFAULT_CFG_PATH
    return None


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
    config = get_config(args.config)
    if config is None:
        logging.error("No config file found ! Exiting now...")
        exit(1)
    my_event_handler = NSWatcher(config_path=config, debug=args.verbose)
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
