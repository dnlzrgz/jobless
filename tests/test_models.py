from faker import Faker
from sqlmodel import Session, select

from jobless.models import Application, Company, Entry

fake = Faker()


def test_cascade_delete_company_to_applications(session: Session):
    """
    Deleting a company should also remove its applications.
    """

    company = Company(name=fake.company())
    first_application = Application(title=fake.sentence(), company=company)
    second_application = Application(title=fake.sentence(), company=company)

    session.add_all([company, first_application, second_application])
    session.commit()

    applications_in_db = session.exec(select(Application)).all()
    assert len(applications_in_db) == 2

    session.delete(company)
    session.commit()

    applications_in_db = session.exec(select(Application)).all()
    assert len(applications_in_db) == 0


def test_application_orphan_entries_cleanup(session: Session):
    """
    Deleting an application should also remove its entries.
    """

    company = Company(name=fake.company())
    application = Application(title=fake.sentence(), company=company)

    first_entry = Entry(content=fake.sentence(), application=application)
    second_entry = Entry(content=fake.sentence(), application=application)

    session.add_all([company, application, first_entry, second_entry])
    session.commit()

    entries_in_db = session.exec(select(Entry)).all()
    assert len(entries_in_db) == 2

    session.delete(application)
    session.commit()

    entries_in_db = session.exec(select(Entry)).all()
    assert len(entries_in_db) == 0
