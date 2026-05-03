from faker import Faker

from jobless import models, schemas
from jobless.enums import Location, Status

fake = Faker()


def make_skill_model() -> models.Skill:
    return models.Skill(
        id=fake.unique.random_int(),
        name=fake.unique.word(),
    )


def make_contact_model() -> models.Contact:
    return models.Contact(
        id=fake.unique.random_int(),
        name=fake.unique.name(),
        email=fake.unique.email(),
        phone=fake.unique.phone_number(),
        url=fake.unique.url(),
    )


def make_company_model() -> models.Company:
    return models.Company(
        id=fake.unique.random_int(),
        name=fake.unique.company(),
        url=fake.unique.url(),
        industry=fake.job(),
    )


def make_application_model() -> models.Application:
    return models.Application(
        id=fake.unique.random_int(),
        title=fake.job(),
        description=fake.paragraph(),
        salary=f"${fake.random_int(50, 200)}k",
        url=fake.unique.url(),
        location_type=fake.random_element(elements=list(Location)),
        status=fake.random_element(elements=list(Status)),
        date_applied=fake.date_between(start_date="-30d", end_date="today"),
        follow_up_date=fake.date_between(start_date="today", end_date="+14d"),
        notes=fake.sentence(),
        company=make_company_model(),
        skills=[make_skill_model() for _ in range(fake.random_int(0, 5))],
        contacts=[make_contact_model() for _ in range(fake.random_int(1, 3))],
    )


def make_skill_schema() -> schemas.Skill:
    return schemas.Skill(
        id=fake.unique.random_int(),
        name=fake.unique.word(),
    )


def make_contact_schema() -> schemas.Contact:
    return schemas.Contact(
        id=fake.unique.random_int(),
        name=fake.unique.name(),
        email=fake.unique.email(),
        phone=fake.unique.phone_number(),
        url=fake.unique.url(),
    )


def make_company_schema() -> schemas.Company:
    return schemas.Company(
        id=fake.unique.random_int(),
        name=fake.unique.company(),
        url=fake.unique.url(),
        industry=fake.job(),
    )


def make_application_schema() -> schemas.Application:
    return schemas.Application(
        id=fake.unique.random_int(),
        title=fake.job(),
        description=fake.paragraph(),
        salary=f"${fake.random_int(50, 200)}k",
        url=fake.unique.url(),
        location_type=fake.random_element(elements=list(Location)),
        status=fake.random_element(elements=list(Status)),
        date_applied=fake.date_between(start_date="-30d", end_date="today"),
        follow_up_date=fake.date_between(start_date="today", end_date="+14d"),
        notes=fake.sentence(),
        company=make_company_schema(),
        skills=[make_skill_schema() for _ in range(fake.random_int(0, 5))],
        contacts=[make_contact_schema() for _ in range(fake.random_int(1, 3))],
    )
