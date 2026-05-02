from sqlalchemy import create_engine, event

from jobless.models import Base


def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA mmap_size = 134217728;")
    cursor.execute("PRAGMA journal_size_limit = 27103364;")
    cursor.execute("PRAGMA cache_size = 2000;")

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
    Base.metadata.create_all(engine)
