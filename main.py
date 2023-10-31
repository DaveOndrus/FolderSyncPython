import argparse
import logging
import time

import keyboard

import utils


def main(argv):
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-s", "--source", help="source file location")
    argParser.add_argument("-r", "--replica", help="replica file location")
    argParser.add_argument("-l", "--logfile", help="log file location")
    argParser.add_argument("-i", "--interval", help="how many seconds wait until next synchronization")

    args = argParser.parse_args()
    print("args=%s" % args)
    print("args.name=%s" % args.source)
    interval = int(args.interval)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[
                            logging.FileHandler(args.logfile),
                            logging.StreamHandler()
                        ])

    """
    after 300 seconds the app will close. Change (timer < 300) to True for not closing the app
    """
    timer = 0
    while timer < 300:
        utils.sync_source_folder_with_replica_folder(args.source, args.replica)
        if keyboard.is_pressed('q'):
            print("Exiting the loop.")
            break
        time.sleep(interval)
        timer = timer + interval


if __name__ == '__main__':
    main('PyCharm')
