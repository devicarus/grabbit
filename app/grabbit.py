from pathlib import Path
from typing import Optional
from logging import Logger
import json
import csv

from praw.models import Submission
from praw import Reddit

from app.downloader import Downloader
from app.typing_custom import PostId, Post


class Grabbit:
    _downloadedPosts: set[PostId] = set()
    _failedDownloads: set[PostId] = set()
    _submissionQueue: list[Submission] = []

    _reddit: Reddit
    _downloader: Downloader

    _wd: Path
    _addedCount = 0

    def __init__(self, reddit: Reddit, logger: Logger):
        self._reddit = reddit
        self._logger = logger

        self._downloader = Downloader(logger)

    def init(self, wd: Path) -> None:
        self._logger.info("Initializing Grabbit...")
        self._wd = wd
        self._wd.mkdir(parents=True, exist_ok=True)

        self._logger.info("Checking for existing data...")
        self._downloadedPosts = self._load_set_from_json(self._wd / "downloaded.json")
        self._failedDownloads = self._load_set_from_json(self._wd / "failed.json")

        if len(self._downloadedPosts) > 0:
            self._logger.info(f"Loaded {len(self._downloadedPosts)} downloaded posts")
        if len(self._failedDownloads) > 0:
            self._logger.info(f"Loaded {len(self._failedDownloads)} failed downloads")

    def load_post_queue(self, csv: Optional[Path]) -> None:
        if csv:
            self._logger.info(f"Getting post queue from file {csv}")
            self._submissionQueue = self._reddit.info(fullnames=self._load_gdpr_saved_posts_csv(csv))
        else:
            self._logger.info("Getting post queue from Reddit")
            self._submissionQueue = self._reddit.user.me().saved(limit=None)

    def run(self, skip_failed: bool = False) -> None:
        self._logger.info("Starting download process...")
        for submission in self._submissionQueue:
            if submission.id in self._downloadedPosts:
                self._logger.info(
                    f"Skipping post {submission.id} from r/{submission.subreddit.display_name} - already downloaded")
                continue

            if skip_failed and submission.id in self._failedDownloads:
                self._logger.info(
                    f"Skipping post {submission.id} from r/{submission.subreddit.display_name} - previously failed")
                continue

            self._logger.debug(f"Parsing submission {submission.id} from r/{submission.subreddit.display_name}")
            submission = self._fix_crosspost(submission)
            post = self._to_post(submission)

            self._logger.debug(post)
            if post.url is None and post.url_preview is None and (post.data == ['[removed]'] or len(post.data) == 0):
                self._logger.info(f"Skipping post {post.id} from r/{post.sub} - no valid data to work with")
                continue

            self._logger.debug(f"Attempting to download post {post.id} from r/{post.sub}")

            target = self._wd / post.sub
            target.mkdir(parents=True, exist_ok=True)
            target = target / post.id

            files = self._downloader.download(post, target)
            if len(files) == 0:
                self._logger.info(f"❌ Failed to download post {post.id} from r/{post.sub}")
                self._failedDownloads.add(post.id)
                continue

            self._save_metadata(post, files, target)

            self._downloadedPosts.add(post.id)
            self._addedCount += 1
            self._logger.info(f"✅ Downloaded post {post.id} from r/{post.sub}")

            if self._addedCount % 10 == 0:
                self.save_all()

    def _save_metadata(self, post: Post, files: list[Path], target: Path) -> None:
        self._logger.debug(files)
        with open(target.with_suffix(".json"), "w") as f:
            json.dump({
                "id": post.id,
                "sub": post.sub,
                "title": post.title,
                "author": post.author,
                "date": post.date,
                "files": [file.name for file in files],
            }, f, indent=4)

    def _to_post(self, submission: Submission) -> Post:
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
        xposts = getattr(post, 'crosspost_parent_list', [])
        if len(xposts) > 0:
            return self._reddit.submission(id=xposts[-1]["id"])
        return post

    def _process_gallery(self, submission: Submission) -> list[str]:
        gallery_data = getattr(submission, 'gallery_data', None)
        if gallery_data is None:
            return []

        # Get links to each image in Reddit gallery
        # Try block to account for possibility of some posts media data not containing "p", "u", etc. elements
        post = vars(submission)
        urls = []
        try:
            ord = [i["media_id"] for i in post["gallery_data"]["items"]]
            for key in ord:
                img = post["media_metadata"][key]
                if len(img["p"]) > 0:
                    url = img["p"][-1]["u"]
                else:
                    url = img["s"]["u"]
                url = url.split("?")[0].replace("preview", "i")
                urls.append(url)
        except Exception:
            return urls

        return urls

    def save_all(self):
        self._logger.info("Saving data...")
        self._save_set_as_json(self._downloadedPosts, self._wd / "downloaded.json")
        self._save_set_as_json(self._failedDownloads, self._wd / "failed.json")

    @staticmethod
    def _save_set_as_json(data: set, path: Path):
        with open(path, "w") as f:
            json.dump(list(data), f, indent=4)

    @staticmethod
    def _load_set_from_json(path: Path) -> set:
        try:
            with open(path, 'r') as f:
                json_dict = json.load(f)
            return set(json_dict)
        except FileNotFoundError:
            return set()

    @staticmethod
    def _load_gdpr_saved_posts_csv(path: Path) -> list[str]:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            ids = [row[0] for row in reader]
            del ids[0]
        names = [id if id.startswith("t3_") else f"t3_{id}" for id in ids]
        return names