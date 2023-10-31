import argparse
import logging
import time

import utils


def main(argv):
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-s", "--source", required=True, help="source file location")
    argParser.add_argument("-r", "--replica", required=True, help="replica file location")
    argParser.add_argument("-l", "--logfile", required=True, help="log file location")
    argParser.add_argument("-i", "--interval", type=utils.check_positive_int, required=True,
                           help="how many seconds wait until next synchronization")

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
    # while True:
    while timer < 300:
        if utils.sync_source_folder_with_replica_folder(args.source, args.replica) != "Source location does not exists":
            time.sleep(interval)
            timer = timer + interval
        else:
            logger = logging.getLogger()
            logger.error("Source location does not exists")
            break


if __name__ == '__main__':
    main('PyCharm')
