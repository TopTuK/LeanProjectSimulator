"""Sign-in with Yandex ID (OAuth 2.0 authorization code flow).

Docs: https://yandex.ru/dev/id/doc/en/codes/code-url and
https://yandex.ru/dev/id/doc/en/user-information. The signed-in user's id
lives in the Starlette session cookie under "uid".
"""

import os
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import models as m
from app.db import get_db

YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID", "")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET", "")
YANDEX_REDIRECT_URI = os.getenv("YANDEX_REDIRECT_URI", "http://localhost:8080/auth/login-yandex")
# without a fixed secret every restart signs everybody out
SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in ("1", "true", "yes")

AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
TOKEN_URL = "https://oauth.yandex.ru/token"
INFO_URL = "https://login.yandex.ru/info"


class YandexError(Exception):
    pass


class YandexClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def authorize_url(self, state: str) -> str:
        query = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
        }
        return f"{AUTHORIZE_URL}?{urlencode(query)}"

    def exchange_code(self, code: str) -> str:
        try:
            r = httpx.post(TOKEN_URL, timeout=10, data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            })
        except httpx.HTTPError as e:
            raise YandexError(str(e)) from e
        if r.status_code != 200 or "access_token" not in r.json():
            raise YandexError(f"token exchange failed: {r.status_code}")
        return r.json()["access_token"]

    def user_info(self, token: str) -> dict:
        try:
            r = httpx.get(INFO_URL, params={"format": "json"}, headers={"Authorization": f"OAuth {token}"}, timeout=10)
        except httpx.HTTPError as e:
            raise YandexError(str(e)) from e
        if r.status_code != 200:
            raise YandexError(f"user info failed: {r.status_code}")
        return r.json()


def get_yandex() -> YandexClient:
    return YandexClient(YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET, YANDEX_REDIRECT_URI)


def safe_next(path: str | None) -> str:
    """Only same-site absolute paths, so the login can't redirect elsewhere."""
    if not path or not path.startswith("/") or path.startswith("//") or "\\" in path:
        return "/"
    return path


def avatar_url(user: m.User) -> str | None:
    if not user.avatar_id:
        return None
    return f"https://avatars.yandex.net/get-yapic/{user.avatar_id}/islands-68"


def user_view(user: m.User) -> dict:
    return {
        "id": user.id,
        "login": user.login,
        "name": user.name or user.login,
        "email": user.email,
        "avatar_url": avatar_url(user),
    }


def current_user(request: Request, db: Session = Depends(get_db)) -> m.User:
    uid = request.session.get("uid")
    user = db.get(m.User, uid) if uid is not None else None
    if user is None:
        raise HTTPException(status_code=401, detail="login required")
    return user
