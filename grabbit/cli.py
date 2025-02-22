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
    help = "to activate debug mode",
)
@click.option(
    "--csv",
    metavar="FILENAME",
    type = Path,
    help = "load Reddit GDPR saved posts export CSV file",
)
@click.option(
    "--skip-failed",
    is_flag = True,
    help = "skip previously failed downloads",
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

    signal.signal(signal.SIGINT, exit_handler)

    with open(user_config, encoding="utf-8") as f:
        config = json.load(f)
        user = RedditUser(**config)

    logger = GrabbitLogger(level=logging.DEBUG if debug else logging.INFO)
    grabbit = Grabbit(user=user, logger=logger)
    logger.set_grabbit(grabbit)
    grabbit.init(output_dir)
    grabbit.load_post_queue(csv)
    grabbit.download_queue(skip_failed=skip_failed)