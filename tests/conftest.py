import pytest
from faker import Faker
from sqlalchemy.orm import Session

from jobless.db import get_engine, init_db
from jobless.mapper import Mapper
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    ContactRepository,
    SkillRepository,
)
from tests.factories import (
    ApplicationFactory,
    CompanyFactory,
    ContactFactory,
    SkillFactory,
)

fake = Faker()


@pytest.fixture
def engine():
    engine = get_engine("sqlite:///:memory:")
    init_db(engine)
    return engine


@pytest.fixture
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection, expire_on_commit=False)

    yield session

    session.close()
    transaction.rollback()

    connection.close()


@pytest.fixture(autouse=True)
def _wire_factories(session):
    for factory_cls in (
        SkillFactory,
        CompanyFactory,
        ContactFactory,
        ApplicationFactory,
    ):
        factory_cls._meta.sqlalchemy_session = session


@pytest.fixture(scope="session")
def mapper():
    return Mapper()


@pytest.fixture
def company_repo(session, mapper):
    return CompanyRepository(session, mapper)


@pytest.fixture
def skill_repo(session, mapper):
    return SkillRepository(session, mapper)


@pytest.fixture
def contact_repo(session, mapper):
    return ContactRepository(session, mapper)


@pytest.fixture
def application_repo(session, mapper):
    return ApplicationRepository(session, mapper)
