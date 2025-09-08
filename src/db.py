import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import PostgresDsn


ENGINE = None


def _init_engine():
    db_url = PostgresDsn.build(
        scheme="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER", "root"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        path=os.getenv("POSTGRES_DB", "excel_parser"),
    )
    global ENGINE
    ENGINE = create_engine(str(db_url), pool_pre_ping=True, future=True)


def _create_session():
    global ENGINE
    if ENGINE is None:
        _init_engine()
    SessionLocal = sessionmaker(
        bind=ENGINE,
        expire_on_commit=False, # no reason to use it, we dont have update logic, so object can be used after commit
        autoflush=True, # default but still goot to set excplicitly
        autocommit=False,  # default but still goot to set excplicitly
    )
    return SessionLocal()


def get_session():
    # Yield a SQLAlchemy Session and always close it
    session = _create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
