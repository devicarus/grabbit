""" This module contains the CLI for Grabbit. """

import json
import signal
import sys
from pathlib import Path
import logging

import click

from grabbit.grabbit import Grabbit
from grabbit.logger import GrabbitLogger
from grabbit.typing_custom import RedditUser
from grabbit.utils import get_version

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
@click.version_option(get_version(), message="%(version)s")
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
    logger.info("Accessing Reddit as user %s", user.username)

    logger.set_grabbit(grabbit)
    signal.signal(signal.SIGINT, exit_handler)

    logger.info("Initializing 🔧")
    grabbit.init(output_dir)

    if csv is not None:
        logger.info("Downloading posts specified in CSV file %s 🚀", csv)
        grabbit.download_csv(csv_path=csv, skip_failed=skip_failed)
    else:
        logger.info("Downloading all Saved Posts 🚀")
        grabbit.download_saved(skip_failed=skip_failed)

    logger.info("Download process completed! 🎉")
