from pathlib import Path
from typing import Optional

from grabbit.utils import guess_media_extension, RequestFailedException
from grabbit.logger import logger
from grabbit.utils.httpclient import http_client


def download_image(url: str, target: Path) -> Optional[Path]:
    try:
        response = http_client.get(url, stream=True)
    except RequestFailedException as e:
        logger.debug("Failed to download image from %s", url, exc_info=e)
        return None

    extension = guess_media_extension(response)
    if extension:
        target = target.with_suffix(extension)
    else:
        logger.warning("Failed to guess extension, using .bin")
        target = target.with_suffix(".bin")

    with open(target, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024 * 1):  # 1 MB
            f.write(chunk)

    return target
