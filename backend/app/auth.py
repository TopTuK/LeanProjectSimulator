"""Sign-in with Yandex ID (OAuth 2.0), VK ID (OAuth 2.1 with PKCE) and
Google (OpenID Connect, code flow with a client secret plus PKCE).

Yandex docs: https://yandex.ru/dev/id/doc/en/codes/code-url and
https://yandex.ru/dev/id/doc/en/user-information. VK ID docs:
https://id.vk.com/about/business/go/docs/ru/vkid/latest/vk-id/connection/api-integration/api-description
- VK ID also signs in Odnoklassniki and Mail.ru accounts. Google docs:
https://developers.google.com/identity/protocols/oauth2/web-server and
https://developers.google.com/identity/openid-connect/openid-connect. The
signed-in user's id lives in the Starlette session cookie under "uid".
"""

import base64
import hashlib
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


VK_CLIENT_ID = os.getenv("VK_CLIENT_ID", "")
VK_REDIRECT_URI = os.getenv("VK_REDIRECT_URI", "http://localhost:8080/auth/login-vk")

VK_AUTHORIZE_URL = "https://id.vk.com/authorize"
VK_TOKEN_URL = "https://id.vk.com/oauth2/auth"
VK_INFO_URL = "https://id.vk.com/oauth2/user_info"
# our provider key -> VK ID "provider" parameter (which account to sign in with)
VK_PROVIDERS = {"vk": "vkid", "ok": "ok_ru", "mail": "mail_ru"}


class VkError(Exception):
    pass


def pkce_pair() -> tuple[str, str]:
    """(code_verifier, S256 code_challenge)"""
    verifier = secrets.token_urlsafe(48)
    digest = hashlib.sha256(verifier.encode()).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


class VkClient:
    """Public client: PKCE plus device_id replace the client secret."""

    def __init__(self, client_id: str, redirect_uri: str):
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    def authorize_url(self, state: str, challenge: str, provider: str = "vk") -> str:
        query = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": "email",
            "provider": VK_PROVIDERS.get(provider, VK_PROVIDERS["vk"]),
        }
        return f"{VK_AUTHORIZE_URL}?{urlencode(query)}"

    def _post(self, url: str, data: dict) -> dict:
        try:
            r = httpx.post(url, data=data, timeout=10)
        except httpx.HTTPError as e:
            raise VkError(str(e)) from e
        try:
            body = r.json()
        except ValueError as e:
            raise VkError(f"bad response: {r.status_code}") from e
        if not isinstance(body, dict):
            raise VkError(f"bad response: {r.status_code}")
        if r.status_code != 200 or "error" in body:
            raise VkError(f"{url} failed: {r.status_code} {body.get('error')}")
        return body

    def exchange_code(self, code: str, verifier: str, device_id: str, state: str) -> str:
        body = self._post(VK_TOKEN_URL, {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": verifier,
            "client_id": self.client_id,
            "device_id": device_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
        })
        if "access_token" not in body:
            raise VkError("token exchange failed: no access_token")
        return body["access_token"]

    def user_info(self, token: str) -> dict:
        body = self._post(VK_INFO_URL, {"client_id": self.client_id, "access_token": token})
        if not isinstance(body.get("user"), dict) or "user_id" not in body["user"]:
            raise VkError("user info failed: no user")
        return body["user"]


def get_vk() -> VkClient:
    return VkClient(VK_CLIENT_ID, VK_REDIRECT_URI)


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/login-google")

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_INFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleError(Exception):
    pass


class GoogleClient:
    """Confidential client: the client secret plus PKCE."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def authorize_url(self, state: str, challenge: str) -> str:
        query = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }
        return f"{GOOGLE_AUTHORIZE_URL}?{urlencode(query)}"

    def _request(self, method: str, url: str, **kwargs) -> dict:
        try:
            r = httpx.request(method, url, timeout=10, **kwargs)
        except httpx.HTTPError as e:
            raise GoogleError(str(e)) from e
        try:
            body = r.json()
        except ValueError as e:
            raise GoogleError(f"bad response: {r.status_code}") from e
        if not isinstance(body, dict):
            raise GoogleError(f"bad response: {r.status_code}")
        if r.status_code != 200 or "error" in body:
            raise GoogleError(f"{url} failed: {r.status_code} {body.get('error')}")
        return body

    def exchange_code(self, code: str, verifier: str) -> str:
        body = self._request("POST", GOOGLE_TOKEN_URL, data={
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": verifier,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        })
        if "access_token" not in body:
            raise GoogleError("token exchange failed: no access_token")
        return body["access_token"]

    def user_info(self, token: str) -> dict:
        body = self._request("GET", GOOGLE_INFO_URL, headers={"Authorization": f"Bearer {token}"})
        if not body.get("sub"):
            raise GoogleError("user info failed: no sub")
        return body


def get_google() -> GoogleClient:
    return GoogleClient(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)


def safe_next(path: str | None) -> str:
    """Only same-site absolute paths, so the login can't redirect elsewhere."""
    if not path or not path.startswith("/") or path.startswith("//") or "\\" in path:
        return "/"
    return path


def avatar_url(user: m.User) -> str | None:
    if not user.avatar_id:
        return None
    if user.avatar_id.startswith(("https://", "http://")):  # VK ID and Google give a full URL
        return user.avatar_id
    return f"https://avatars.yandex.net/get-yapic/{user.avatar_id}/islands-68"


def provider_of(user: m.User) -> str:
    if user.google_id:
        return "google"
    return "vk" if user.vk_id else "yandex"


def user_view(user: m.User) -> dict:
    return {
        "id": user.id,
        "provider": provider_of(user),
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
