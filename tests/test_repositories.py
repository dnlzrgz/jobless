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
            company=LookupSchema(
                id=company.id,
                label=company.name,
            ),
        ),
    )
    assert isinstance(application, ApplicationSchema)
    assert application.id
    assert application.title
    assert application.company.id == company.id


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


def test_company_repository_update_name(faker, company_repository):
    original_name = faker.unique.company()
    company = company_repository.add(
        CompanySchema(name=original_name),
    )

    new_name = faker.unique.company()
    update_data = CompanySchema(id=company.id, name=new_name)
    updated_schema = company_repository.update(update_data)
    assert updated_schema.name != original_name
    assert updated_schema.name == new_name


def test_company_repository_update_contacts(
    faker,
    contact_repository,
    company_repository,
):
    contact = contact_repository.add(ContactSchema(name=faker.name()))
    contact_lookup = LookupSchema(id=contact.id, label=contact.name)

    company = company_repository.add(
        CompanySchema(
            name=faker.unique.company(),
            contacts=[contact_lookup],
        )
    )

    update_schema = CompanySchema(
        id=company.id,
        name=company.name,
        contacts=[],
    )

    updated_schema = company_repository.update(update_schema)
    assert updated_schema.id == company.id
    assert not updated_schema.contacts
    assert len(updated_schema.contacts) == 0


def test_application_repository_update_company(
    faker,
    company_repository,
    application_repository,
):
    first_company = company_repository.add(
        CompanySchema(
            name=faker.unique.company(),
        )
    )
    second_company = company_repository.add(
        CompanySchema(
            name=faker.unique.company(),
        )
    )

    application = application_repository.add(
        ApplicationSchema(
            title=faker.job(),
            company=LookupSchema(id=first_company.id, label=first_company.name),
        )
    )
    assert application.company.id == first_company.id

    update_schema = ApplicationSchema(
        id=application.id,
        title=application.title,
        company=LookupSchema(id=second_company.id, label=second_company.name),
    )

    updated_schema = application_repository.update(update_schema)
    assert updated_schema.id == application.id
    assert updated_schema.company
    assert updated_schema.company.id == second_company.id


def test_contact_repository_update_email(faker, contact_repository):
    original_email = faker.unique.email()
    contact = contact_repository.add(
        ContactSchema(
            name=faker.name(),
            email=original_email,
        ),
    )

    new_email = faker.unique.email()
    update_data = ContactSchema(id=contact.id, name=contact.name, email=new_email)
    updated_schema = contact_repository.update(update_data)
    assert updated_schema.email != original_email
    assert updated_schema.email == new_email


def test_contact_repository_update_empty_name_fails(faker, contact_repository):
    contact = contact_repository.add(
        ContactSchema(name=faker.name()),
    )

    update_data = ContactSchema(id=contact.id, name="")
    with pytest.raises(ValueError):
        contact_repository.update(update_data)


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
                "company": LookupSchema(id=company.id, label=company.name),
                "skills": skills,
                "contacts": [contact],
            }
        )
    )

    application = application_repository.get_with_details(application.id)
    assert application
    assert isinstance(application, ApplicationSchema)
    assert application.company.id == company.id
    assert application.company.label == company.name
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
