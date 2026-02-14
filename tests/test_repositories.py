import pytest

from jobless.models import Skill
from jobless.schemas import (
    ApplicationSchema,
    CompanySchema,
    ContactSchema,
    LookupSchema,
    SkillSchema,
)


def test_skill_repository_add(faker, skill_repository):
    skill_name = faker.word()
    new_skill = skill_repository.add(Skill(name=skill_name))
    assert isinstance(new_skill, SkillSchema)
    assert new_skill.id
    assert new_skill.name == skill_name


def test_skill_repository_add_fails_silently_if_duplicated(faker, skill_repository):
    skill_name = faker.word()
    new_skill = skill_repository.add(Skill(name=skill_name))
    assert isinstance(new_skill, SkillSchema)
    assert new_skill.id
    assert new_skill.name == skill_name

    repeated_skill = skill_repository.add(Skill(name=skill_name))
    assert isinstance(repeated_skill, SkillSchema)
    assert repeated_skill.id
    assert repeated_skill.name == skill_name


def test_application_repository_add(faker, company_repository, application_repository):
    company = company_repository.add(
        CompanySchema(name=faker.company()),
    )
    assert isinstance(company, CompanySchema)
    assert company.id

    application = application_repository.add(
        ApplicationSchema(
            title=faker.job(),
            company_id=company.id,
        ),
    )
    assert isinstance(application, ApplicationSchema)
    assert application.id
    assert application.title
    assert application.company_id == company.id


def test_contact_repository_add(faker, company_repository, contact_repository):
    company = company_repository.add(
        CompanySchema(name=faker.company()),
    )
    assert isinstance(company, CompanySchema)
    assert company.id

    contact = contact_repository.add(
        ContactSchema(
            name=faker.name(),
            companies=[LookupSchema(id=company.id, label=company.name)],
            email=faker.email(),
        ),
    )
    assert isinstance(contact, ContactSchema)
    assert contact.id
    assert contact.name
    assert len(contact.companies) == 1


def test_contact_repository_add_should_fail_if_bad_email(faker, contact_repository):
    with pytest.raises(ValueError):
        contact_repository.add(
            ContactSchema(
                name=faker.name(),
                email="invalid",
            ),
        )


def test_skill_repository_get_by_id(faker, skill_repository):
    skill_name = faker.word()
    skill = skill_repository.add(SkillSchema(name=skill_name))
    assert isinstance(skill, SkillSchema)
    assert skill.id
    assert skill.name == skill_name

    lookup_skill = skill_repository.get_by_id(skill.id)
    assert isinstance(lookup_skill, LookupSchema)
    assert lookup_skill.id
    assert lookup_skill.label == skill_name


def test_skill_repository_list(skill_repository):
    skill_names = {"python", "javascript", "c", "tdd", "rust"}
    for name in skill_names:
        skill_repository.add(SkillSchema(name=name))

    skills = skill_repository.list()
    assert len(skills) == len(skills)

    for skill in skills:
        assert isinstance(skill, LookupSchema)
        assert skill.label in skill_names


def test_skill_repository_delete(faker, skill_repository):
    skill_name = faker.name()
    skill = skill_repository.add(Skill(name=skill_name))
    assert isinstance(skill, SkillSchema)
    assert skill.id

    skill_repository.delete(skill.id)
    skill = skill_repository.get_by_id(skill.id)
    assert not skill


# def test_update(skill_repository):
#     skill = skill_repository.add(Skill(name="python"))
#     updated = skill_repository.update(skill.name, {"name": "rust"})
#
#     assert updated
#     assert updated.name == "rust"
#
#
def test_get_application_with_details(
    faker,
    company_repository,
    contact_repository,
    skill_repository,
    application_repository,
):
    company = company_repository.add(
        CompanySchema(
            name=faker.company(),
        ),
    )

    contact = contact_repository.add(
        ContactSchema.from_dict(
            {
                "name": faker.name(),
                "companies": [company],
            },
        )
    )

    skills = []
    skill_names = {"python", "javascript", "c", "tdd", "rust"}
    for name in skill_names:
        skill = skill_repository.add(SkillSchema(name=name))
        skills.append(skill)

    application = application_repository.add(
        ApplicationSchema.from_dict(
            {
                "title": faker.job(),
                "company_id": company.id,
                "skills": skills,
                "contacts": [contact],
            }
        )
    )

    application = application_repository.get_with_details(application.id)
    assert application
    assert isinstance(application, ApplicationSchema)
    assert application.company_id == company.id
    assert hasattr(application, "skills")
    assert len(application.skills) == len(skills)
    assert hasattr(application, "contacts")
    assert len(application.contacts) == 1


def test_company_repository_list_names(company_repository, faker):
    companies = [CompanySchema(name=faker.name()) for _ in range(10)]
    for company in companies:
        company_repository.add(company)

    names = company_repository.list_names()
    assert names
    assert len(names) == len(names)


def test_company_repository_list_urls(company_repository, faker):
    companies = [
        CompanySchema(
            name=faker.name(),
            url=faker.unique.url(),
        )
        for _ in range(10)
    ]
    for company in companies:
        company_repository.add(company)

    # add contact without email just in case.
    company_repository.add(CompanySchema(name=faker.name()))

    urls = company_repository.list_urls()
    assert urls
    assert len(urls) == len(urls)


def test_contact_repository_list_emails(contact_repository, faker):
    contacts = [
        ContactSchema(name=faker.name(), email=faker.unique.email()) for _ in range(10)
    ]
    for contact in contacts:
        contact_repository.add(contact)

    # add contact without email just in case.
    contact_repository.add(ContactSchema(name=faker.name()))

    emails = contact_repository.list_emails()
    assert emails
    assert len(emails) == len(contacts)


def test_contact_repository_list_phones(contact_repository, faker):
    contacts = [
        ContactSchema(name=faker.name(), phone=faker.unique.phone_number())
        for _ in range(10)
    ]
    for contact in contacts:
        contact_repository.add(contact)

    # add contact without phone just in case.
    contact_repository.add(ContactSchema(name=faker.name()))

    phones = contact_repository.list_phones()
    assert phones
    assert len(phones) == len(contacts)


def test_contact_repository_list_urls(contact_repository, faker):
    contacts = [
        ContactSchema(name=faker.name(), url=faker.unique.url()) for _ in range(10)
    ]
    for contact in contacts:
        contact_repository.add(contact)

    # add contact without url just in case.
    contact_repository.add(ContactSchema(name=faker.name()))

    urls = contact_repository.list_urls()
    assert urls
    assert len(urls) == len(contacts)
