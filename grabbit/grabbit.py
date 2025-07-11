""" This module contains the main Grabbit class."""

from json import JSONDecodeError
from pathlib import Path
from typing import Iterator
import json

from praw.exceptions import RedditAPIException, ClientException
from praw.models import Submission
from praw import Reddit
from prawcore import OAuthException

from grabbit.downloader import get_downloader
from grabbit.typing_custom import RedditAccount, PostStatus, DownloadOptions
from grabbit.utils import load_gdpr_saved_posts_csv, safe_generator, branch_counter
from grabbit.logger import logger


class Grabbit:
    """ The main Grabbit class. """
    _posts: dict[str, PostStatus] = {}

    _reddit: Reddit

    _wd: Path
    _added_count = 0

    def __init__(self, user: RedditAccount):
        self._reddit = Reddit(
            user_agent = "Grabbit - Saved Posts Downloader",
            username=user.username,
            password=user.password,
            client_id = user.client_id,
            client_secret = user.client_secret
        )

    def logged_in(self):
        """ Returns True if the user credentials are correct, False otherwise. """
        try:
            self._reddit.user.me()
            return True
        except OAuthException:
            return False

    def init(self, wd: Path) -> None:
        """ Initializes the Grabbit instance. """
        logger.debug("Initializing Grabbit working directory")
        self._wd = wd
        self._wd.mkdir(parents=True, exist_ok=True)

        logger.debug("Checking for existing data")
        self._load()

    def exit(self) -> None:
        """ Saves the current state of the Grabbit instance. """
        self._save()


    def download_csv(self, csv_path: Path, options: DownloadOptions) -> None:
        """ Downloads the posts specified in the CSV file. """
        self._run(self._reddit.info(fullnames=load_gdpr_saved_posts_csv(csv_path)), options)

    def download_saved(self, options: DownloadOptions) -> None:
        """ Downloads all Saved Posts. """
        self._run(self._reddit.user.me().saved(limit=None), options)


    def _should_skip_known(self, submission: Submission, skip_failed: bool) -> bool:
        match self._posts.get(submission.id):
            case PostStatus.DOWNLOADED:
                logger.info("Skipping post %s from r/%s - already downloaded", submission.id,
                                  submission.subreddit.display_name)
                return True
            case PostStatus.SKIPPED:
                logger.info("Skipping post %s from r/%s - no valid data to work with", submission.id,
                                  submission.subreddit.display_name)
                return True
            case PostStatus.FAILED if skip_failed:
                logger.info("Skipping post %s from r/%s - previously failed", submission.id,
                                  submission.subreddit.display_name)
                return True
            case _:
                return False


    @safe_generator(
        exceptions=(RedditAPIException, ClientException),
        handler=lambda e: logger.error("Reddit API error while preprocessing, skipped: %s", e, exc_info=True),
    )
    def _submission_filter(self, get_next: Iterator[Submission], skip_failed: bool) -> Iterator[Submission]:
        for submission in get_next:
            if not isinstance(submission, Submission):
                logger.info("Skipping %s - not a post", submission.id)
                self._posts[submission.id] = PostStatus.SKIPPED
                continue

            if self._should_skip_known(submission, skip_failed):
                continue

            logger.debug("Processing submission %s from r/%s (https://reddit.com%s)", submission.id, submission.subreddit.display_name, submission.permalink)
            original_submission = self._fix_crosspost(submission)
            if original_submission.id != submission.id:
                logger.debug("Post %s recognised as crosspost of %s", submission.id, original_submission.id)
                if self._should_skip_known(original_submission, skip_failed):
                    continue

            if submission.selftext in ['[removed]', '[ Removed by Reddit in response to a copyright notice. ]', '[ Removed by Reddit on account of violating the [content policy](/help/contentpolicy). ]']:
                logger.info("Skipping post %s from r/%s - no valid data to work with", submission.id, submission.subreddit.display_name)
                self._posts[submission.id] = PostStatus.SKIPPED
                continue

            yield submission

    def _run(self, get_next: Iterator, options: DownloadOptions) -> None:
        for post in self._submission_filter(get_next, options.skip_failed):
            self._download(post)

            if self._added_count % options.save_every == 0:
                self._save()

        self._save()

    def _download(self, submission: Submission) -> None:
        logger.debug("Attempting to download post %s from r/%s", submission.id, submission.subreddit.display_name)

        target = self._wd / submission.subreddit.display_name
        target.mkdir(parents=True, exist_ok=True)
        target = target / submission.id

        if not get_downloader(submission).download(submission, target):
            logger.info("❌ Failed to download post %s from r/%s", submission.id, submission.subreddit.display_name)
            self._posts[submission.id] = PostStatus.FAILED
            return

        self._posts[submission.id] = PostStatus.DOWNLOADED

        self._added_count += 1
        logger.info("✅ Downloaded post %s from r/%s", submission.id, submission.subreddit.display_name)


    def total_posts(self):
        """ Returns the total number of posts in the database. """
        return len(self._posts)

    def added_posts(self):
        """ Returns the number of posts added to the database by the Grabbit instance. """
        return self._added_count

    def _fix_crosspost(self, post: Submission) -> Submission:
        try:
            crossposts = getattr(post, 'crosspost_parent_list', [])
            if len(crossposts) > 0:
                return self._reddit.submission(id=crossposts[-1]["id"])
        # pylint: disable=broad-except
        except Exception as e:
            branch_counter.record("fix_crosspost_fail")
            logger.error("Failed to resolve crosspost, falling back to original post", exc_info=e)
        return post

    def _save(self):
        with open(self._wd / "db.json", "w", encoding="utf-8") as file:
            # noinspection PyTypeChecker
            json.dump(self._posts, file, indent=4)

    def _load(self):
        try:
            with open(self._wd / "db.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self._posts = dict(data)
        except (FileNotFoundError, JSONDecodeError):
            pass
