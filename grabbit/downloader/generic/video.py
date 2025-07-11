from pathlib import Path
from time import sleep
from typing import Optional
from urllib.parse import urlparse

from yt_dlp import YoutubeDL, DownloadError

from grabbit.utils import NullLogger
from grabbit.logger import logger


def download_video(url: str, target: Path, max_tries: int = 3) -> Optional[Path]:
    with YoutubeDL({
        "outtmpl": f"{target}.%(ext)s",
        "logger": NullLogger()
    }) as ydl:
        retry_count = 0
        while retry_count < max_tries:
            logger.debug("Attempting download using YTDL")
            try:
                status = ydl.download([url])
                if status != 0:
                    logger.warning("YTDL exited with non-zero status, but no exception was raised")

                filename = next(
                    (file for file in target.parent.iterdir() if file.stem == target.stem and file.suffix != ".json"),
                    None)
                if filename is None:
                    logger.warning("YTDL exited with zero status, but no file was found")
                return filename
            except Exception as e:
                if isinstance(e, DownloadError):
                    logger.debug("YTDL download error: %s", e.msg)
                    if e.msg and ("HTTP Error 404" in e.msg or "HTTP Error 410" in e.msg):
                        logger.debug("Resource gone, won't retry")
                        return None

                    if e.msg and "Unsupported URL" in e.msg:
                        logger.warning("Unsupported URL, won't retry")
                        return None

                    retry_count += 1
                    if retry_count < max_tries:
                        if urlparse(url).hostname == "web.archive.org" and e.msg and 'Errno 61' in e.msg:
                            logger.debug("Rate limited, cooling off for a minute")
                            sleep(61)
                    continue
                raise

    return None
