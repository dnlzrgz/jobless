import pytest

from jobless.schemas import Application, Company, Contact, Skill
from tests import factories


def test_skill_name_validation():
    with pytest.raises(ValueError):
        Skill(id=1, name="   ")


def test_company_name_validation():
    with pytest.raises(ValueError):
        Company(id=1, name="   ")


def test_application_title_validation():
    with pytest.raises(ValueError):
        Application(
            id=1,
            title="\n\t",
            company=factories.CompanyFactory.build(),
        )


def test_contact_email_validation():
    contact = Contact(id=1, name="John Doe", email="valid@example.com")
    assert contact.email == "valid@example.com"

    with pytest.raises(ValueError):
        Contact(id=1, name="John Doe", email="not valid")
