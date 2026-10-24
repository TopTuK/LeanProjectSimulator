import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.auth import (
    VK_PROVIDERS,
    VkClient,
    VkError,
    YandexClient,
    YandexError,
    current_user,
    get_vk,
    get_yandex,
    pkce_pair,
    safe_next,
    user_view,
)
from app.db import get_db
from app.models import utcnow

router = APIRouter(tags=["auth"])


def _start(request: Request, next: str | None) -> str:
    state = secrets.token_urlsafe(24)
    request.session["oauth_state"] = state
    request.session["oauth_next"] = safe_next(next)
    return state


def _check_state(expected: str | None, code: str | None, state: str | None) -> None:
    if not code or not state or not expected or not secrets.compare_digest(state, expected):
        raise HTTPException(status_code=400, detail="invalid oauth state")


def _sign_in(request: Request, user: m.User, next_path: str) -> RedirectResponse:
    request.session.clear()
    request.session["uid"] = user.id
    return RedirectResponse(next_path, status_code=302)


@router.get("/api/auth/yandex/login")
def login(request: Request, next: str | None = None, yandex: YandexClient = Depends(get_yandex)):
    return RedirectResponse(yandex.authorize_url(_start(request, next)), status_code=302)


@router.get("/auth/login-yandex")
def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
    yandex: YandexClient = Depends(get_yandex),
):
    """Redirect URI registered in the Yandex OAuth app."""
    expected = request.session.pop("oauth_state", None)
    next_path = request.session.pop("oauth_next", "/")
    if error:
        return RedirectResponse("/?auth_error=1", status_code=302)
    _check_state(expected, code, state)
    try:
        info = yandex.user_info(yandex.exchange_code(code))
    except YandexError:
        return RedirectResponse("/?auth_error=1", status_code=302)

    yandex_id = str(info["id"])
    user = db.scalar(select(m.User).where(m.User.yandex_id == yandex_id))
    if user is None:
        user = m.User(yandex_id=yandex_id)
        db.add(user)
    user.login = info.get("login")
    user.email = info.get("default_email")
    user.name = info.get("display_name") or info.get("real_name")
    user.avatar_id = None if info.get("is_avatar_empty", True) else info.get("default_avatar_id")
    user.last_login_at = utcnow()
    db.commit()
    return _sign_in(request, user, next_path)


@router.get("/api/auth/vk/login")
def vk_login(
    request: Request, next: str | None = None, provider: str = "vk", vk: VkClient = Depends(get_vk),
):
    """provider: vk | ok (Odnoklassniki) | mail (Mail.ru), all through VK ID."""
    state = _start(request, next)
    verifier, challenge = pkce_pair()
    request.session["oauth_verifier"] = verifier
    provider = provider if provider in VK_PROVIDERS else "vk"
    return RedirectResponse(vk.authorize_url(state, challenge, provider), status_code=302)


@router.get("/auth/login-vk")
def vk_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    device_id: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
    vk: VkClient = Depends(get_vk),
):
    """Redirect URI registered in the VK ID app."""
    expected = request.session.pop("oauth_state", None)
    next_path = request.session.pop("oauth_next", "/")
    verifier = request.session.pop("oauth_verifier", None)
    if error:
        return RedirectResponse("/?auth_error=1", status_code=302)
    _check_state(expected, code, state)
    if not verifier or not device_id:
        raise HTTPException(status_code=400, detail="invalid oauth state")
    try:
        info = vk.user_info(vk.exchange_code(code, verifier, device_id, state))
    except VkError:
        return RedirectResponse("/?auth_error=1", status_code=302)

    vk_id = str(info["user_id"])
    user = db.scalar(select(m.User).where(m.User.vk_id == vk_id))
    if user is None:
        user = m.User(vk_id=vk_id)
        db.add(user)
    user.name = " ".join(p for p in (info.get("first_name"), info.get("last_name")) if p) or None
    user.email = info.get("email") or None
    user.avatar_id = info.get("avatar") or None
    user.last_login_at = utcnow()
    db.commit()
    return _sign_in(request, user, next_path)


@router.get("/api/auth/me")
def me(user: m.User = Depends(current_user)):
    return user_view(user)


@router.post("/api/auth/logout", status_code=204)
def logout(request: Request):
    request.session.clear()
    return Response(status_code=204)
