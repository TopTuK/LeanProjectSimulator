import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, MetaData, inspect, text
from sqlalchemy.exc import OperationalError
from starlette.middleware.sessions import SessionMiddleware

from app.auth import COOKIE_SECURE, SESSION_SECRET
from app.db import SessionLocal, engine
from app.engine.sim import SimError
from app.models import Base, User
from app.routers import auth, scenarios, sessions
from app.seed import seed


def _rebuild_sqlite_users(eng: Engine, old_columns: set[str]) -> None:
    """SQLite can't drop NOT NULL, so copy users into a table built from the model."""
    new = User.__table__.to_metadata(MetaData(), name="users_new")
    keep = ", ".join(c.name for c in new.columns if c.name in old_columns)
    with eng.begin() as conn:
        new.create(conn)
        conn.execute(text(f"INSERT INTO users_new ({keep}) SELECT {keep} FROM users"))
        conn.execute(text("DROP TABLE users"))
        conn.execute(text("ALTER TABLE users_new RENAME TO users"))


def upgrade_schema(eng: Engine = engine) -> None:
    """create_all() never alters tables, so add columns introduced after the first deploy."""
    columns = {c["name"] for c in inspect(eng).get_columns("sessions")}
    if "user_id" not in columns:
        with eng.begin() as conn:
            conn.execute(text("ALTER TABLE sessions ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_sessions_user_id ON sessions (user_id)"))

    # VK ID sign-in: users get vk_id, and yandex_id becomes optional
    users = {c["name"]: c for c in inspect(eng).get_columns("users")}
    if "yandex_id" in users and not users["yandex_id"]["nullable"]:
        if eng.dialect.name == "sqlite":
            _rebuild_sqlite_users(eng, set(users))
        else:
            with eng.begin() as conn:
                conn.execute(text("ALTER TABLE users ALTER COLUMN yandex_id DROP NOT NULL"))
    if "vk_id" not in {c["name"] for c in inspect(eng).get_columns("users")}:
        with eng.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN vk_id VARCHAR(64)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_vk_id ON users (vk_id)"))
    # Google sign-in
    if "google_id" not in {c["name"] for c in inspect(eng).get_columns("users")}:
        with eng.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(64)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id)"))


def init_db(retries: int = 30) -> None:
    for attempt in range(retries):
        try:
            Base.metadata.create_all(engine)
            upgrade_schema()
            break
        except OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(1)
    with SessionLocal() as db:
        seed(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="SimulTrain demo API", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware, secret_key=SESSION_SECRET, session_cookie="simultrain_session",
    same_site="lax", https_only=COOKIE_SECURE, max_age=30 * 24 * 3600,
)
app.include_router(auth.router)
app.include_router(scenarios.router)
app.include_router(sessions.router)


@app.exception_handler(SimError)
async def sim_error(_: Request, exc: SimError):
    return JSONResponse(status_code=exc.status, content={"detail": exc.message})


@app.get("/api/health")
def health():
    return {"ok": True}
