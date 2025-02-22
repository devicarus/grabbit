import argparse
import json
import signal
import sys
from pathlib import Path
import logging

from app.grabbit import Grabbit
from app.logger import GrabbitLogger
from app.typing_custom import RedditUser

def main(args):
    def exit_handler(*_):
        logger.info("Ctrl+C detected! Saving data before exit...")
        grabbit.exit()
        sys.exit(0)

    signal.signal(signal.SIGINT, exit_handler)

    with open(args.user_config, encoding="utf-8") as f:
        config = json.load(f)
        user = RedditUser(**config)

    logger = GrabbitLogger(level=logging.DEBUG if args.debug else logging.INFO)
    grabbit = Grabbit(user=user, logger=logger)
    logger.set_grabbit(grabbit)
    grabbit.init(args.output_directory)
    grabbit.load_post_queue(args.csv)
    grabbit.download_queue(skip_failed=args.skip_failed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Grabbit - Reddit Saved Posts Downloader")
    parser.add_argument(
        "output_directory",
        type = Path,
        help = "output directory for downloaded media with metadata",
    )
    parser.add_argument(
        "user_config",
        type = Path,
        help = "path to user configuration file",
    )
    parser.add_argument(
        "--debug", "-d",
        action = "store_true",
        help = "to activate debug mode",
    )
    parser.add_argument(
        "--csv",
        metavar="FILENAME",
        type = Path,
        help = "load Reddit GDPR saved posts export CSV file",
    )
    parser.add_argument(
        "--skip-failed",
        action = "store_true",
        help = "skip previously failed downloads",
    )

    main(parser.parse_args())
