from contextlib import contextmanager
from typing import Generator

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from jobless import models  # noqa: F401


def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA busy_timeout = 5000;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA mmap_size = 268435456;")
    cursor.execute("PRAGMA journal_size_limit = 5242880;")
    cursor.execute("PRAGMA cache_size = 2000;")
    cursor.execute("PRAGMA temp_store = MEMORY;")

    cursor.close()


def get_engine(db_url: str, connect_args: dict | None = None):
    if not connect_args:
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        db_url,
        connect_args=connect_args,
    )

    event.listen(engine, "connect", set_sqlite_pragmas)

    return engine


def init_db(engine) -> None:
    """
    Initializes all tables.
    """

    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session(engine) -> Generator[Session, None, None]:
    session = Session(engine)

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
