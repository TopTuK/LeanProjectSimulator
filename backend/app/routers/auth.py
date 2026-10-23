import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.auth import YandexClient, YandexError, current_user, get_yandex, safe_next, user_view
from app.db import get_db
from app.models import utcnow

router = APIRouter(tags=["auth"])


@router.get("/api/auth/yandex/login")
def login(request: Request, next: str | None = None, yandex: YandexClient = Depends(get_yandex)):
    state = secrets.token_urlsafe(24)
    request.session["oauth_state"] = state
    request.session["oauth_next"] = safe_next(next)
    return RedirectResponse(yandex.authorize_url(state), status_code=302)


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
    if not code or not state or not expected or not secrets.compare_digest(state, expected):
        raise HTTPException(status_code=400, detail="invalid oauth state")
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

    request.session.clear()
    request.session["uid"] = user.id
    return RedirectResponse(next_path, status_code=302)


@router.get("/api/auth/me")
def me(user: m.User = Depends(current_user)):
    return user_view(user)


@router.post("/api/auth/logout", status_code=204)
def logout(request: Request):
    request.session.clear()
    return Response(status_code=204)
