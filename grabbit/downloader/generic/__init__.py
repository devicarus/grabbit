from pathlib import Path
from typing import Optional

from grabbit.utils.httpclient import RequestFailedException, http_client
from grabbit.typing_custom import MediaType
from grabbit.utils.wayback import wayback
from grabbit.logger import logger

from .image import download_image
from .video import download_video


def _follow_redirects(url: str) -> str:
    try:
        response = http_client.head(url, allow_redirects=True, timeout=10, max_tries=1)
        response.raise_for_status()
        return response.url.split("?")[0]
    except RequestFailedException:
        return url

def _get_generic_download_function(media_type: MediaType.IMAGE or MediaType.VIDEO) -> callable:
    if media_type == MediaType.IMAGE:
        return download_image
    if media_type == MediaType.VIDEO:
        return download_video
    raise ValueError(f"Unsupported media type: {type}")

def download(url: str, target: Path, media_type: MediaType.IMAGE or MediaType.VIDEO) -> Optional[Path]:
    """ Downloads media from a generic URL. """
    download_function = _get_generic_download_function(media_type)

    logger.debug("Attempting regular download: %s", url)
    result = download_function(url, target)
    if result is not None:
        return result

    redirected_url = _follow_redirects(url)
    if redirected_url != url:
        logger.debug("Attempting download from redirected URL: %s", redirected_url)
        result = download_function(redirected_url, target)
        if result is not None:
            return result

    logger.debug("Attempting download from Wayback Machine")
    wayback_urls = wayback.get(url)
    if len(wayback_urls) == 0:
        logger.debug("No Wayback Machine captures found")
    for (count, wayback_url) in enumerate(wayback_urls):
        logger.debug("Attempting wayback machine download %d/%d: %s", count + 1, len(wayback_urls), wayback_url)
        file = download_function(url, target)
        if file is not None:
            return file

    return None
