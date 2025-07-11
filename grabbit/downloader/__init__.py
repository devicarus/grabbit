from praw.models import Submission

from .modules import Downloader
from .modules.gallery import GalleryDownloader
from .modules.generic import GenericDownloader
from .modules.media_source import MediaSourceDownloader
from .modules.selfpost import SelfpostDownloader

def get_downloader(submission: Submission) -> type[Downloader]:
    for downloader in [GalleryDownloader, SelfpostDownloader, MediaSourceDownloader]:
        if downloader.supports(submission):
            return downloader
    return GenericDownloader
