import pytest

from jobless.enums import Location, Status
from jobless.schemas import Application, Company, Contact, Skill


def test_skill_name_validation():
    with pytest.raises(ValueError):
        Skill(id=1, name="   ")


def test_company_name_validation():
    with pytest.raises(ValueError):
        Company(id=1, name="   ")


def test_application_title_validation():
    from tests.factories import make_company_schema

    with pytest.raises(ValueError):
        Application(
            id=1,
            title="\n\t",
            company=make_company_schema(),
        )


def test_contact_email_validation():
    contact = Contact(id=1, name="John Doe", email="valid@example.com")
    assert contact.email == "valid@example.com"

    with pytest.raises(ValueError):
        Contact(id=1, name="John Doe", email="not valid")


def test_minimal_application_creation():
    from tests.factories import make_company_schema

    application = Application(
        id=1,
        title="Software Engineer",
        company=make_company_schema(),
    )
    assert application.status == Status.SAVED
    assert application.location_type == Location.ON_SITE
