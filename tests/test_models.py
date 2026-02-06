import pytest
from sqlalchemy import select

from jobless.models import Application, Company, Contact


def test_delete_company_cascades_to_applications(session, faker):
    company = Company(name=faker.company())

    Application(title=faker.job(), company=company)
    Application(title=faker.job(), company=company)

    session.add(company)
    session.commit()

    total_applications = session.scalars(select(Application)).all()
    assert len(total_applications) == 2

    session.delete(company)
    session.commit()

    remaining_applications = session.scalars(select(Application)).all()
    assert len(remaining_applications) == 0


def test_invalid_contact_email_raises_exception(faker):
    with pytest.raises(ValueError):
        Contact(name=faker.name(), email="wrong")
