""" Tests for the Post.good method """
# @generated [partially] GPT-4o: prompt: Write pytest unit tests for the Post.good method

from grabbit.typing_custom import Post

def test_good_with_url():
    """ Test that a post with a URL is considered good """
    post = Post(id="1", sub="test", title="Test Post", author="author", date=1234567890, url="https://example.com")
    assert post.good() is True

def test_good_with_url_preview():
    """ Test that a post with a URL preview is considered good """
    post = Post(id="2", sub="test", title="Test Post", author="author", date=1234567890, url_preview="https://example.com/preview")
    assert post.good() is True

def test_good_with__data():
    """ Test that a post with data is considered good """
    post = Post(id="3", sub="test", title="Test Post", author="author", date=1234567890, data=["Some content"])
    assert post.good() is True

def test_good_without_data():
    """ Test that a post with empty, or removed data is not considered good """
    post = Post(id="4", sub="test", title="Test Post", author="author", date=1234567890, data=["[removed]"])
    assert post.good() is False
    post = Post(id="5", sub="test", title="Test Post", author="author", date=1234567890, data=["[ Removed by Reddit in response to a copyright notice. ]"])
    assert post.good() is False
    post = Post(id="6", sub="test", title="Test Post", author="author", date=1234567890, data=[])
    assert post.good() is False
