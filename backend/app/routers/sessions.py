import asyncio
import json

from anyio import to_thread
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models as m
from app import schemas
from app.auth import current_user
from app.db import SessionLocal, get_db
from app.engine import sim

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _tick(db: Session, session_id: str, user: m.User):
    """Lock the user's session row and bring its clock up to date."""
    s = sim.load_session(db, session_id, lock=True, owner_id=user.id)
    sim.advance(db, s)
    return s


def _act(db: Session, user: m.User, session_id: str, client_action_id: str | None, name: str, payload: dict, fn) -> dict:
    s = _tick(db, session_id, user)
    if not sim.seen_action(db, s, client_action_id):
        fn(s)
        sim.log_action(db, s, name, payload, client_action_id)
    db.commit()
    return sim.build_state(db, s)


@router.post("", status_code=201)
def create(body: schemas.SessionCreate, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    s = sim.create_session(db, body.model_dump(), user_id=user.id)
    return sim.build_state(db, s)


@router.get("/{session_id}")
def get(session_id: str, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    s = _tick(db, session_id, user)
    db.commit()
    return sim.build_state(db, s)


@router.get("/{session_id}/snapshots")
def get_snapshots(session_id: str, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    s = _tick(db, session_id, user)
    db.commit()
    return sim.snapshots(db, s)


@router.post("/{session_id}/clock/start")
def start(session_id: str, body: schemas.Action | None = None, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    cid = body.client_action_id if body else None
    return _act(db, user, session_id, cid, "start", {}, lambda s: sim.start(db, s))


@router.post("/{session_id}/clock/pause")
def pause(session_id: str, body: schemas.Action | None = None, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    cid = body.client_action_id if body else None
    return _act(db, user, session_id, cid, "pause", {}, lambda s: sim.pause(db, s))


@router.put("/{session_id}/assignments")
def put_assignments(session_id: str, body: schemas.AssignmentsIn, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    items = [a.model_dump() for a in body.assignments]
    return _act(db, user, session_id, body.client_action_id, "assign", {"assignments": items},
                lambda s: sim.set_assignments(db, s, items))


@router.post("/{session_id}/leveling")
def leveling(session_id: str, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    s = _tick(db, session_id, user)
    db.commit()
    return sim.propose_leveling(db, s)


@router.post("/{session_id}/messages/{message_id}/read")
def read_message(session_id: str, message_id: int, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    return _act(db, user, session_id, None, "read", {"message": message_id}, lambda s: sim.mark_read(db, s, message_id))


@router.post("/{session_id}/decisions/{decision_id}")
def decide(session_id: str, decision_id: int, body: schemas.DecisionIn, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    return _act(db, user, session_id, body.client_action_id, "decide", {"decision": decision_id, "option": body.option},
                lambda s: sim.decide(db, s, decision_id, body.option))


@router.get("/{session_id}/stream")
async def stream(session_id: str, request: Request, user: m.User = Depends(current_user)):
    """Server-sent events: the full state once a second while the client listens."""

    def snapshot() -> dict:
        with SessionLocal() as db:
            s = _tick(db, session_id, user)
            db.commit()
            return sim.build_state(db, s)

    first = await to_thread.run_sync(snapshot)  # 404 before the stream starts

    async def events():
        state = first
        while True:
            yield f"data: {json.dumps(state)}\n\n"
            await asyncio.sleep(1)
            if await request.is_disconnected():
                break
            state = await to_thread.run_sync(snapshot)

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
