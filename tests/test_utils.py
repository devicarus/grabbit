""" Tests for the utils module functions """
# @generated [partially] GPT-4o: Prompt: Write pytest unit tests for these functions.

from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch, mock_open
from requests.models import Response

from grabbit.utils import guess_media_type, guess_media_extension, load_gdpr_saved_posts_csv, ensure_post_id, NullLogger, get_version
from grabbit.typing_custom import MediaType

def test_guess_media_type():
    """ Tests the guess_media_type function """
    response = Response()

    response.headers["content-type"] = "image/jpeg"
    assert guess_media_type(response) == MediaType.IMAGE

    response.headers["content-type"] = "video/mp4"
    assert guess_media_type(response) == MediaType.VIDEO

    response.headers["content-type"] = "application/json"
    assert guess_media_type(response) == MediaType.UNKNOWN

def test_guess_media_extension():
    """ Tests the guess_media_extension function """
    response = Response()

    response.headers["content-type"] = "image/jpeg"
    assert guess_media_extension(response) == ".jpg"

    response.headers["content-type"] = "video/mp4"
    assert guess_media_extension(response) == ".mp4"

    response.headers["content-type"] = "application/json"
    assert guess_media_extension(response) == ".json"

def test_load_gdpr_saved_posts_csv():
    """ Tests the load_gdpr_saved_posts_csv function """
    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', newline='') as temp_file:
        temp_file.write("\n".join([
            "id,permalink",
            "12345,https://www.reddit.com/r/aww/comments/12345",
            "t3_67890,https://www.reddit.com/r/aww/comments/67890",
            "abcde,https://www.reddit.com/r/aww/comments/abcde"
        ]))
        temp_file_path = Path(temp_file.name)

    expected_ids = ["t3_12345", "t3_67890", "t3_abcde"]
    assert load_gdpr_saved_posts_csv(temp_file_path) == expected_ids

def test_ensure_post_id_with_prefix():
    """ Test case where post_id_like already starts with "t3_ """
    post_id_like = "t3_abc123"
    expected = "t3_abc123"
    assert ensure_post_id(post_id_like) == expected

def test_ensure_post_id_without_prefix():
    """ Test case where post_id_like does not start with "t3_ """
    post_id_like = "abc123"
    expected = "t3_abc123"
    assert ensure_post_id(post_id_like) == expected

def test_null_logger(capsys):
    """ Tests the NullLogger class """
    logger = NullLogger()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    captured = capsys.readouterr()
    assert captured.out == ""

def test_get_version():
    """ Tests the get_version function """
    mock_toml_content = b"""
    [project]
    version = "1.0.0"
    """
    with patch('builtins.open', mock_open(read_data=mock_toml_content)):
        assert get_version() == "1.0.0"
