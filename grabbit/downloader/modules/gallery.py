from mimetypes import guess_extension
from pathlib import Path
from typing import Optional

from praw.models import Submission

from grabbit.downloader import Downloader
from grabbit.downloader.generic.image import download_image
from grabbit.logger import logger
from grabbit.typing_custom import PostType


class GalleryDownloader(Downloader):
    """ Downloader for gallery posts. """

    @staticmethod
    def supports(submission: Submission) -> bool:
        return getattr(submission, "is_gallery", False)

    @staticmethod
    def download_media(submission: Submission, target: Path) -> (Optional[PostType], list[Path]):
        target.mkdir(parents=True, exist_ok=True)

        files: list[Path] = []
        urls = GalleryDownloader._process_gallery(submission)
        for (n, url) in enumerate(urls):
            file = download_image(url, target / str(n))
            if file:
                files.append(file)
                logger.debug(f"Downloaded item from album {target.name}: {n + 1}/{len(urls)}")
            else:
                logger.debug(f"Failed to download item from album {target.name}: {n + 1}/{len(urls)}")

        if len(files) == 0:
            return None, []
        return PostType.IMAGE_GALLERY, files

    @staticmethod
    def _process_gallery(submission: Submission) -> list[str]:
        try:
            gallery_data = getattr(submission, 'gallery_data')
        except AttributeError:
            return []

        if gallery_data is None:
            return []

        urls = []
        for media_id in [item["media_id"] for item in gallery_data["items"]]:
            img = getattr(submission, "media_metadata")[media_id]
            extension = guess_extension(img["m"], strict=False).removeprefix(".")
            if extension in img["s"]:
                url = img["s"][extension]
            else:
                url = img["s"]["u"]
            urls.append(url)

        return urls
