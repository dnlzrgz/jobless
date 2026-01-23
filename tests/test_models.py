from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from jobless.models import Application, Company

fake = Faker()


def test_delete_company_cascades_to_applications(session: Session):
    """
    Deleting a company should also remove its applications.
    """

    company = Company(name=fake.company())

    Application(title=fake.job(), company=company)
    Application(title=fake.job(), company=company)

    session.add(company)
    session.commit()

    total_applications = session.scalars(select(Application)).all()
    assert len(total_applications) == 2

    session.delete(company)
    session.commit()

    remaining_applications = session.scalars(select(Application)).all()
    assert len(remaining_applications) == 0
