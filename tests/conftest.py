import pytest

from jobless.db import get_connection, init_db


@pytest.fixture
def db_conn():
    db_url = ":memory:"
    with get_connection(db_url) as conn:
        init_db(conn)
        yield conn
