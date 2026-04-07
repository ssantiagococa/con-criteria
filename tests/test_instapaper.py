import pytest
import responses
from src.instapaper import InstapaperClient


@responses.activate
def test_authenticate_returns_token():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    client = InstapaperClient(
        consumer_key="key", consumer_secret="secret",
        username="user@example.com", password="pass"
    )
    assert client.token == "mytoken"
    assert client.token_secret == "mytokensecret"


@responses.activate
def test_get_folder_id_returns_correct_id():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/folders/list",
        json=[
            {"folder_id": 1234, "title": "hot-topic"},
            {"folder_id": 5678, "title": "aprende"},
        ],
        status=200,
    )
    client = InstapaperClient("key", "secret", "user@example.com", "pass")
    assert client.get_folder_id("hot-topic") == 1234
    assert client.get_folder_id("aprende") == 5678


@responses.activate
def test_get_bookmarks_returns_list():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/list",
        json=[
            {"type": "bookmark", "bookmark_id": 1, "title": "Article 1",
             "url": "https://example.com/1", "description": "Excerpt 1"},
            {"type": "user"},
        ],
        status=200,
    )
    client = InstapaperClient("key", "secret", "user@example.com", "pass")
    bookmarks = client.get_bookmarks(folder_id=1234, limit=3)
    assert len(bookmarks) == 1
    assert bookmarks[0]["title"] == "Article 1"


@responses.activate
def test_archive_bookmark():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/archive",
        json=[{"type": "bookmark", "bookmark_id": 42}],
        status=200,
    )
    client = InstapaperClient("key", "secret", "user@example.com", "pass")
    client.archive_bookmark(42)  # Should not raise
