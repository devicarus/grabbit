from pathlib import Path
from typing import Optional

from praw.models import Submission
from yt_dlp.extractor import gen_extractors

from grabbit.downloader import Downloader
from grabbit.downloader.generic import download
from grabbit.typing_custom import PostType, MediaType


class YtDlpDownloader(Downloader):

    @staticmethod
    def supports(submission: Submission) -> bool:
        for extractor in gen_extractors():
            if extractor.suitable(submission.url) and extractor.IE_NAME != 'generic':
                return True
        return False

    @staticmethod
    def download_media(submission: Submission, target: Path) -> (Optional[PostType], list[Path]):
        file = download(submission.url, target, MediaType.VIDEO)
        if file is not None:
            return PostType.VIDEO, [file]
        return None, []
