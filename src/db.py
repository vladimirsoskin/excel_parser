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
        expire_on_commit=False,  # TODO add description why
        autoflush=True,
        autocommit=False,  # TODO why ???
        future=True,  # TODO why ???
    )
    return SessionLocal()


# def init_schema() -> None: TODO how to use it?
#     """Run once at startup (or use Alembic migrations)."""
#     Base.metadata.create_all(_engine)


def get_session():
    """Yield a SQLAlchemy Session and always close it."""
    session = _create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
