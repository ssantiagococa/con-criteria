from urllib.parse import parse_qs
import requests
from requests_oauthlib import OAuth1


class InstapaperClient:
    BASE_URL = "https://www.instapaper.com/api/1"

    def __init__(self, consumer_key, consumer_secret, username, password):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token, self.token_secret = self._authenticate(username, password)

    def _authenticate(self, username, password):
        auth = OAuth1(self.consumer_key, self.consumer_secret)
        response = requests.post(
            f"{self.BASE_URL}/oauth/access_token",
            auth=auth,
            data={
                "x_auth_username": username,
                "x_auth_password": password,
                "x_auth_mode": "client_auth",
            },
        )
        response.raise_for_status()
        params = parse_qs(response.text)
        return params["oauth_token"][0], params["oauth_token_secret"][0]

    def _auth(self):
        return OAuth1(
            self.consumer_key, self.consumer_secret,
            self.token, self.token_secret
        )

    def get_folder_id(self, folder_name):
        response = requests.post(
            f"{self.BASE_URL}/folders/list", auth=self._auth()
        )
        response.raise_for_status()
        for folder in response.json():
            if folder.get("title") == folder_name:
                return folder["folder_id"]
        raise ValueError(f"Folder '{folder_name}' not found in Instapaper")

    def get_bookmarks(self, folder_id, limit=10):
        response = requests.post(
            f"{self.BASE_URL}/bookmarks/list",
            auth=self._auth(),
            data={"folder_id": folder_id, "limit": limit},
        )
        response.raise_for_status()
        return [b for b in response.json() if b.get("type") == "bookmark"]

    def archive_bookmark(self, bookmark_id):
        response = requests.post(
            f"{self.BASE_URL}/bookmarks/archive",
            auth=self._auth(),
            data={"bookmark_id": bookmark_id},
        )
        response.raise_for_status()
