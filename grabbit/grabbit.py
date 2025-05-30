""" This module contains the main Grabbit class."""

from json import JSONDecodeError
from mimetypes import guess_extension
from pathlib import Path
from typing import Iterator
from logging import Logger
import json

from praw.models import Submission
from praw import Reddit
from prawcore import OAuthException

from grabbit.downloader import Downloader
from grabbit.typing_custom import PostId, Post, RedditUser, PostStatus
from grabbit.utils import load_gdpr_saved_posts_csv, NullLogger


class Grabbit:
    """ The main Grabbit class. """
    _posts: dict[PostId, PostStatus] = {}

    _reddit: Reddit
    _downloader: Downloader

    _wd: Path
    _added_count = 0

    def __init__(self, user: RedditUser, logger: Logger | None):
        self._reddit = Reddit(
            user_agent = "Grabbit - Saved Posts Downloader",
            username=user.username,
            password=user.password,
            client_id = user.client_id,
            client_secret = user.client_secret
        )

        self._logger = logger if logger else NullLogger()

        self._downloader = Downloader(self._logger)

    def logged_in(self):
        """ Returns True if the user credentials are correct, False otherwise. """
        try:
            self._reddit.user.me()
            return True
        except OAuthException:
            return False

    def init(self, wd: Path) -> None:
        """ Initializes the Grabbit instance. """
        self._logger.debug("Initializing Grabbit working directory")
        self._wd = wd
        self._wd.mkdir(parents=True, exist_ok=True)

        self._logger.debug("Checking for existing data")
        self._load()

    def exit(self) -> None:
        """ Saves the current state of the Grabbit instance. """
        self._save()


    def download_csv(self, csv_path: Path, skip_failed: bool = False) -> None:
        """ Downloads the posts specified in the CSV file. """
        self._download(self._submission_filter(self._reddit.info(fullnames=load_gdpr_saved_posts_csv(csv_path)), skip_failed=skip_failed))

    def download_saved(self, skip_failed: bool = False) -> None:
        """ Downloads all Saved Posts. """
        self._download(self._submission_filter(self._reddit.user.me().saved(limit=None), skip_failed=skip_failed))


    def _submission_filter(self, get_next: Iterator, skip_failed: bool) -> Iterator[Post]:
        for submission in get_next:
            if not isinstance(submission, Submission):
                self._logger.info("Skipping %s - not a post", submission.id)
                self._posts[submission.id] = PostStatus.SKIPPED
                continue

            if submission.id in self._posts:
                match self._posts[submission.id]:
                    case PostStatus.DOWNLOADED:
                        self._logger.info("Skipping post %s from r/%s - already downloaded", submission.id, submission.subreddit.display_name)
                        continue
                    case PostStatus.SKIPPED:
                        self._logger.info("Skipping post %s from r/%s - no valid data to work with", submission.id, submission.subreddit.display_name)
                        continue
                    case PostStatus.FAILED if skip_failed:
                        self._logger.info("Skipping post %s from r/%s - previously failed", submission.id, submission.subreddit.display_name)
                        continue

            self._logger.debug("Parsing submission %s from r/%s (https://reddit.com%s)", submission.id, submission.subreddit.display_name, submission.permalink)
            original_submission = self._fix_crosspost(submission)
            post = self._to_post(original_submission)

            self._logger.debug(post)
            if not post.good():
                self._logger.info("Skipping post %s from r/%s - no valid data to work with", post.id, post.sub)
                self._posts[post.id] = PostStatus.SKIPPED
                continue

            yield post

    def _download(self, get_next: Iterator[Post]) -> None:
        for post in get_next:
            self._logger.debug("Attempting to download post %s from r/%s", post.id, post.sub)

            target = self._wd / post.sub
            target.mkdir(parents=True, exist_ok=True)
            target = target / post.id

            files = self._downloader.download(post, target)
            if len(files) == 0:
                self._logger.info("❌ Failed to download post %s from r/%s", post.id, post.sub)
                self._posts[post.id] = PostStatus.FAILED
                continue

            self._save_metadata(post, files, target)

            self._posts[post.id] = PostStatus.DOWNLOADED

            self._added_count += 1
            self._logger.info("✅ Downloaded post %s from r/%s", post.id, post.sub)

            if self._added_count % 10 == 0:
                self._save()

        self._save()

    def total_posts(self):
        """ Returns the total number of posts in the database. """
        return len(self._posts)

    def added_posts(self):
        """ Returns the number of posts added to the database by the Grabbit instance. """
        return self._added_count

    @staticmethod
    def _save_metadata(post: Post, files: list[Path], target: Path) -> None:
        with open(target.with_suffix(".json"), "w", encoding="utf-8") as file:
            # noinspection PyTypeChecker
            json.dump({
                "id": post.id,
                "sub": post.sub,
                "title": post.title,
                "author": post.author,
                "date": post.date,
                "files": [str(file.relative_to(target.parent)) for file in files],
            }, file, indent=4)

    def _to_post(self, submission: Submission) -> Post:
        data: list[str] = []
        if submission.is_self:
            data = [submission.selftext]
        elif "reddit.com/gallery/" in submission.url:
            data = self._process_gallery(submission)

        return Post(
            submission.id,
            submission.subreddit.display_name,
            submission.title,
            submission.author.name if submission.author else "[deleted]",
            submission.created_utc,
            submission.url if submission.url != '' else None,
            getattr(submission, 'preview', {"images": [{"source": {"url": None}}]})["images"][0]["source"]["url"],
            getattr(submission, 'domain', None),
            data
        )

    def _fix_crosspost(self, post: Submission) -> Submission:
        crossposts = getattr(post, 'crosspost_parent_list', [])
        if len(crossposts) > 0:
            return self._reddit.submission(id=crossposts[-1]["id"])
        return post

    def _process_gallery(self, submission: Submission) -> list[str]:
        try:
            gallery_data = getattr(submission, 'gallery_data')
        except AttributeError:
            return []

        if gallery_data is None:
            return []

        urls = []
        for media_id in [item["media_id"] for item in gallery_data["items"]]:
            try:
                img = getattr(submission, "media_metadata")[media_id]
            except AttributeError:
                self._logger.warning("Media metadata missing for media_id %s", media_id)
                continue

            extension = guess_extension(img["m"], strict=False).removeprefix(".")
            if extension in img["s"]:
                url = img["s"][extension]
            else:
                url = img["s"]["u"]
            urls.append(url)

        return urls

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
