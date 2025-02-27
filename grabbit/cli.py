import json
import signal
import sys
from pathlib import Path
import logging

import click

from grabbit.grabbit import Grabbit
from grabbit.logger import GrabbitLogger
from grabbit.typing_custom import RedditUser

@click.command()
@click.argument("output_dir", type = Path)
@click.argument("user_config", type = Path)
@click.option(
    "--debug", "-d",
    is_flag = True,
    help = "Turn on activate debug mode.",
)
@click.option(
    "--csv",
    metavar="FILENAME",
    type = Path,
    help = "Use Reddit GDPR saved posts export CSV file.",
)
@click.option(
    "--skip-failed",
    is_flag = True,
    help = "Skip previously failed downloads.",
)
def cli(output_dir: Path, user_config: Path, debug: bool, csv: Path, skip_failed: bool):
    """
    OUTPUT_DIR is the directory where the downloaded files will be saved
    USER_CONFIG is the path to a JSON file containing Reddit user credentials
    """
    def exit_handler(*_):
        logger.info("Ctrl+C detected! Saving data before exit...")
        grabbit.exit()
        sys.exit(0)

    logger = GrabbitLogger(level=logging.DEBUG if debug else logging.INFO)

    logger.info("Welcome to Grabbit! 🐰")

    logger.debug("Reading user configuration")
    with open(user_config, encoding="utf-8") as f:
        config = json.load(f)
        user = RedditUser(**config)

    grabbit = Grabbit(user=user, logger=logger)
    if not grabbit.logged_in():
        logger.error("Failed to log in to Reddit, check your credentials")
        sys.exit(1)
    logger.info(f"Logged in to Reddit as user {user.username}")

    logger.set_grabbit(grabbit)
    signal.signal(signal.SIGINT, exit_handler)

    grabbit.init(output_dir)
    grabbit.load_post_queue(csv)

    logger.info("Starting download process 🚀")
    grabbit.download_queue(skip_failed=skip_failed)
    logger.info("Download process completed! 🎉")
