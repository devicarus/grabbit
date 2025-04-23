""" This module contains the Downloader class. """

from __future__ import unicode_literals
from pathlib import Path
from time import sleep
from typing import Optional
from logging import Logger

from praw.models.reddit.base import urlparse
from requests import HTTPError
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from grabbit.utils import guess_media_type, guess_media_extension, NullLogger
from grabbit.typing_custom import Post, MediaType
from grabbit.wayback import Wayback
from grabbit.httpclient import HTTPClient, RetryLimitExceededException

# pylint: disable=too-few-public-methods
# This is by design. While it potentially could be a single function,
# Downloader being a class allows it to hold its instances of Logger, HTTPClient and Wayback
# making the usage more concise and readable than passing those as arguments of a function.
class Downloader:
    """ Handles downloading media from Reddit. """
    _headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0"}

    _sources = {
        "image": [
            "i.redd.it",
            "reddit.com",
            "i.redgifs.com"
        ],
        "video": [
            "youtube.com",
            "youtu.be",
            "v.redd.it",
            "redgifs.com",
            "v3.redgifs.com",
            "gfycat.com"
        ]
    }

    _logger: Logger
    _http_client: HTTPClient
    _wayback: Wayback

    def __init__(self, logger: Logger):
        self._logger = logger
        self._http_client = HTTPClient(self._headers, logger)
        self._wayback = Wayback(self._http_client)

    def download(self, post: Post, target: Path) -> list[Path]:
        """ Attempts to download the media from the post. """
        if post.url:
            self._logger.debug(f"Attempting regular download: {post.url}")
            files = self._download_media(post, post.url, target)
            if len(files) > 0:
                return files

            redirected_url = self._follow_redirects(post.url)
            if redirected_url != post.url:
                self._logger.debug(f"Attempting download from redirected URL: {redirected_url}")
                files = self._download_media(post, redirected_url, target)
                if len(files) > 0:
                    return files

            self._logger.debug("Attempting download from Wayback Machine")
            urls = self._wayback.get(post.url)
            if len(urls) == 0:
                self._logger.debug("No Wayback Machine captures found")
            for (count, url) in enumerate(urls):
                self._logger.debug(f"Attempting wayback machine download {count + 1}/{len(urls)}: {url}")
                # noinspection PyTypeChecker
                files = self._download_media(post, url, target)
                if len(files) > 0:
                    return files

        if post.url_preview and post.source in self._sources["image"] and len(post.data) <= 1:
            self._logger.debug("Attempting downloading cashed Reddit image: {post.url_preview}")
            files = self._download_media(post, post.url_preview, target)
            if len(files) > 0:
                return files

        return []

    def _download_media(self, post: Post, url: str, target: Path) -> list[Path]:
        # Workaround for dead imgur links,
        # because they replace the image with a placeholder image that ultimately gets downloaded otherwise.
        if self._follow_redirects(url) in ["https://i.imgur.com/removed.png", "https://imgur.com/"]:
            self._logger.debug("Dead Imgur link")
            return []

        match self._get_media_type(post, url):
            case MediaType.IMAGE:
                path = self._download_generic_image(url, target)
                return [path] if path is not None else []
            case MediaType.GALLERY:
                return self._download_album(post.data, target)
            case MediaType.VIDEO:
                path = self._download_video(url, target)
                return [path] if path is not None else []
            case MediaType.TEXT:
                return [self._download_text(post.data, target)]

        return []

    def _get_media_type(self, post: Post, url: str) -> MediaType:
        if post.source in self._sources["video"]:
            self._logger.debug("Video source detected")
            return MediaType.VIDEO

        if "reddit.com/gallery/" in url:
            self._logger.debug("Gallery detected")
            return MediaType.GALLERY

        if post.source in self._sources["image"]:
            self._logger.debug("Image source detected")
            return MediaType.IMAGE

        if post.source and post.source.startswith("self."):
            self._logger.debug("Text post detected")
            return MediaType.TEXT

        self._logger.debug("Unknown source, trying to guess post format")
        response = self._http_client.head(url, allow_redirects=True)
        guess = guess_media_type(response)
        if guess is MediaType.UNKNOWN:
            self._logger.debug("Failed to guess post format")
        else:
            self._logger.debug("Guessed format as %s", guess.name.lower())
        return guess

    def _download_generic_image(self, url: str, target: Path) -> Optional[Path]:
        with self._http_client.get(url, stream=True) as response:
            if response.status_code != 200:
                return None

            extension = guess_media_extension(response)
            if extension:
                target = target.with_suffix(extension)
            else:
                self._logger.warning("Failed to guess extension, using .bin")
                target = target.with_suffix(".bin")

            with open(target, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024 * 1):  # 1 MB
                    f.write(chunk)

        return target

    @staticmethod
    def _download_text(data: list[str], target: Path) -> Path:
        target = target.with_suffix(".md")
        with open(target, "w", encoding="utf-8") as f:
            f.write("\n".join(data))

        return target

    def _download_video(self, url: str, target: Path, max_tries: int = 3) -> Optional[Path]:
        with YoutubeDL({
            "outtmpl": f"{target}.%(ext)s",
            "logger": NullLogger()
        }) as ydl:
            retry_count = 0
            while retry_count < max_tries:
                self._logger.debug("Attempting download using YTDL")
                try:
                    status = ydl.download([url])
                    if status != 0:
                        self._logger.warning("YTDL exited with non-zero status, but no exception was raised")

                    filename = next((file for file in target.parent.iterdir() if file.stem == target.stem and file.suffix != ".json"), None)
                    if filename is None:
                        self._logger.warning("YTDL exited with zero status, but no file was found")
                    return filename
                except Exception as e:
                    if isinstance(e, DownloadError):
                        self._logger.debug(f"YTDL download error: {e.msg}")
                        if e.msg and ("HTTP Error 404" in e.msg or "HTTP Error 410" in e.msg):
                            self._logger.debug("Resource gone, won't retry")
                            return None

                        if e.msg and "Unsupported URL" in e.msg:
                            self._logger.warning("Unsupported URL, won't retry")
                            return None

                        retry_count += 1
                        if retry_count < max_tries:
                            if urlparse(url).hostname == "web.archive.org" and e.msg and 'Errno 61' in e.msg:
                                self._logger.debug("Rate limited, cooling off for a minute")
                                sleep(61)
                        continue
                    raise

        return None

    def _download_album(self, urls: list[str], target: Path) -> list[Path]:
        if len(urls) == 0:
            return []

        target.mkdir(parents=True, exist_ok=True)

        files: list[Path] = []
        for (count, url) in enumerate(urls):
            file = self._download_generic_image(url, target / str(count))
            if file:
                files.append(file)
                self._logger.debug(f"Downloaded item from album {target.name}: {count+1}/{len(urls)}")
            else:
                self._logger.debug(f"Failed to download item from album {target.name}: {count+1}/{len(urls)}")

        return files

    def _follow_redirects(self, url: str) -> str:
        try:
            response = self._http_client.head(url, allow_redirects=True, timeout=10, max_tries=1)
            response.raise_for_status()
            return response.url.split("?")[0]
        except (RetryLimitExceededException, HTTPError):
            return url
