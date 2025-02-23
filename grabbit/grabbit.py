from mimetypes import guess_extension
from pathlib import Path
from typing import Optional
from logging import Logger
import json

from praw.models import Submission
from praw import Reddit

from grabbit.downloader import Downloader
from grabbit.typing_custom import PostId, Post, RedditUser, PostStatus
from grabbit.utils import load_gdpr_saved_posts_csv, NullLogger


class Grabbit:
    posts: dict[PostId, PostStatus] = {}

    _submissionQueue: list[Submission] = []

    _reddit: Reddit
    _downloader: Downloader

    _wd: Path
    added_count = 0

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

    def init(self, wd: Path) -> None:
        self._logger.info("Initializing Grabbit...")
        self._wd = wd
        self._wd.mkdir(parents=True, exist_ok=True)

        self._logger.info("Checking for existing data...")
        self._load()

        if len(self.posts) > 0:
            self._logger.info(f"Loaded status of {len(self.posts)} posts")

    def exit(self) -> None:
        self._save()

    def load_post_queue(self, csv_path: Optional[Path]) -> None:
        if csv_path:
            self._logger.info(f"Getting post queue from file {csv_path}")
            # noinspection PyTypeChecker
            self._submissionQueue = self._reddit.info(fullnames=load_gdpr_saved_posts_csv(csv_path))
        else:
            self._logger.info("Getting post queue from Reddit")
            self._submissionQueue = self._reddit.user.me().saved(limit=None)

    def download_queue(self, skip_failed: bool = False) -> None:
        self._logger.info("Starting download process...")
        for submission in self._submissionQueue:
            if submission.id in self.posts:
                match self.posts[submission.id]:
                    case PostStatus.DOWNLOADED:
                        self._logger.info(f"Skipping post {submission.id} from r/{submission.subreddit.display_name} - already downloaded")
                        continue
                    case PostStatus.SKIPPED:
                        self._logger.info(f"Skipping post {submission.id} from r/{submission.subreddit.display_name} - no valid data to work with")
                        continue
                    case PostStatus.FAILED if skip_failed:
                        self._logger.info(f"Skipping post {submission.id} from r/{submission.subreddit.display_name} - previously failed")
                        continue

            self._logger.debug(f"Parsing submission {submission.id} from r/{submission.subreddit.display_name} (https://reddit.com{submission.permalink})")
            original_submission = self._fix_crosspost(submission)
            post = self._to_post(original_submission)

            self._logger.debug(post)
            if not post.good():
                self._logger.info(f"Skipping post {post.id} from r/{post.sub} - no valid data to work with")
                self.posts[post.id] = PostStatus.SKIPPED
                continue

            self._logger.debug(f"Attempting to download post {post.id} from r/{post.sub}")

            target = self._wd / post.sub
            target.mkdir(parents=True, exist_ok=True)
            target = target / post.id

            files = self._downloader.download(post, target)
            if len(files) == 0:
                self._logger.info(f"❌ Failed to download post {post.id} from r/{post.sub}")
                self.posts[post.id] = PostStatus.FAILED
                continue

            self._save_metadata(post, files, target)

            self.posts[original_submission.id] = PostStatus.DOWNLOADED
            if submission.id != original_submission.id: # If the post is a crosspost, add the crosspost id as well
                self.posts[submission.id] = PostStatus.DOWNLOADED

            self.added_count += 1
            self._logger.info(f"✅ Downloaded post {post.id} from r/{post.sub}")

            if self.added_count % 10 == 0:
                self._save()

        self._save()

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
        try: # TODO: Remove after testing
            getattr(submission, 'url_overridden_by_dest')
            if submission.url != submission.url_overridden_by_dest:
                self._logger.warning("url_overridden_by_dest != url")
                self._logger.debug(f"url_overridden_by_dest: {submission.url_overridden_by_dest}")
                self._logger.debug(f"url: {submission.url}")
        except AttributeError:
            pass

        url: str = getattr(submission, 'url_overridden_by_dest', submission.url)

        data: list[str] = []
        if submission.is_self:
            data = [submission.selftext]
        elif "reddit.com/gallery/" in url:
            data = self._process_gallery(submission)

        return Post(
            submission.id,
            submission.subreddit.display_name,
            submission.title,
            submission.author.name if submission.author else "[deleted]",
            submission.created_utc,
            url if url != '' else None,
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
                self._logger.warning(f"Media metadata missing for media_id {media_id}")
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
            json.dump(self.posts, file, indent=4)

    def _load(self):
        try:
            with open(self._wd / "db.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.posts = dict(data)
        except FileNotFoundError:
            pass