import pytest
from sqlmodel import Session

from jobless.db import get_engine, init_db


@pytest.fixture
def session():
    engine = get_engine(db_url="sqlite:///:memory:")
    init_db(engine)

    with Session(engine) as session:
        yield session
