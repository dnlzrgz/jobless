import pytest
from sqlalchemy.orm import sessionmaker

from jobless.db import get_engine, init_db
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    ContactRepository,
    SkillRepository,
)


@pytest.fixture
def db_engine():
    engine = get_engine(db_url="sqlite:///:memory:")
    init_db(engine)
    return engine


@pytest.fixture
def session_factory(db_engine):
    return sessionmaker(bind=db_engine, expire_on_commit=False)


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture
def skill_repository(session_factory):
    return SkillRepository(session_factory)


@pytest.fixture
def company_repository(session_factory):
    return CompanyRepository(session_factory)


@pytest.fixture
def contact_repository(session_factory):
    return ContactRepository(session_factory)


@pytest.fixture
def application_repository(session_factory):
    return ApplicationRepository(session_factory)
