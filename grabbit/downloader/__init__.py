from praw.models import Submission

from .modules import Downloader
from .modules.reddit_gallery_downloader import RedditGalleryDownloader
from .modules.generic_downloader import GenericDownloader
from .modules.media_source_downloader import MediaSourceDownloader
from .modules.reddit_selfpost_downloader import RedditSelfpostDownloader
from .modules.yt_dlp_downloader import YtDlpDownloader


def get_downloader(submission: Submission) -> type[Downloader]:
    result = GenericDownloader
    for downloader in [RedditGalleryDownloader, RedditSelfpostDownloader, MediaSourceDownloader, YtDlpDownloader]:
        if downloader.supports(submission):
            result = downloader
            break

    return result
