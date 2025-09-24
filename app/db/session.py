from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = getattr(settings, "database_url", None) or "sqlite:///./local.db"

# For sqlite, need check_same_thread=False if using same connection in threads
engine_kwargs = {
	"pool_pre_ping": True,
	"pool_recycle": 3600,
	"future": True,
}
if DATABASE_URL.startswith("sqlite"):
	engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
	DATABASE_URL,
	**engine_kwargs,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
