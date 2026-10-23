from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.db import get_db

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


@router.get("")
def list_scenarios(db: Session = Depends(get_db)):
    return [
        {"code": s.code, "title": s.title, "description": s.description, "weeks": s.weeks}
        for s in db.scalars(select(m.Scenario).order_by(m.Scenario.code))
    ]
