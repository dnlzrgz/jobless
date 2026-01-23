import pytest
from sqlalchemy.orm import sessionmaker

from jobless.db import get_engine, init_db


@pytest.fixture
def session():
    engine = get_engine(db_url="sqlite:///:memory:")
    init_db(engine)

    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session
