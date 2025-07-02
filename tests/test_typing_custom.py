""" Tests for the Post.good method """
# @generated [partially] GPT-4o: prompt: Write pytest unit tests for the Post.good method

from grabbit.typing_custom import Post, Subreddit


def test_good_with_url():
    """ Test that a post with a URL is considered good """
    post = Post(id="1", subreddit=Subreddit("123abc", "test"), title="Test Post", date=1234567890, url="https://example.com", author=None, url_preview=None, source=None)
    assert post.good() is True

def test_good_with_url_preview():
    """ Test that a post with a URL preview is considered good """
    post = Post(id="2", subreddit=Subreddit("123abc", "test"), title="Test Post", date=1234567890, url_preview="https://example.com/preview", author=None, source=None, url=None)
    assert post.good() is True

def test_good_with__data():
    """ Test that a post with data is considered good """
    post = Post(id="3", subreddit=Subreddit("123abc", "test"), title="Test Post", date=1234567890, data=["Some content"], author=None, url=None, url_preview=None, source=None)
    assert post.good() is True

def test_good_without_data():
    """ Test that a post with empty, or removed data is not considered good """
    post = Post(id="4", subreddit=Subreddit("123abc", "test"), title="Test Post", date=1234567890, data=["[removed]"], author=None, url=None, url_preview=None, source=None)
    assert post.good() is False
    post = Post(id="5", subreddit=Subreddit("123abc", "test"), title="Test Post", date=1234567890, data=["[ Removed by Reddit in response to a copyright notice. ]"], author=None, url=None, url_preview=None, source=None)
    assert post.good() is False
    post = Post(id="6", subreddit=Subreddit("123abc", "test"), title="Test Post", date=1234567890, data=[], author=None, url=None, url_preview=None, source=None)
    assert post.good() is False
