from jobless.models import Application, Company, Contact, Skill, Status


def test_add(faker, skill_repository):
    skill_name = faker.word()
    skill = skill_repository.add(Skill(name=skill_name))

    assert skill
    assert skill.name == skill_name


def test_get_by_id(faker, skill_repository):
    skill_name = faker.word()
    skill_repository.add(Skill(name=skill_name))

    skill_in_db = skill_repository.get_by_id(skill_name)
    assert skill_in_db
    assert skill_in_db.name == skill_name


def test_get_all(skill_repository):
    skills = [Skill(name=name) for name in {"python", "javascript", "c", "tdd", "rust"}]
    for skill in skills:
        skill_repository.add(skill)

    skills_in_db = skill_repository.get_all()
    assert len(skills_in_db) == len(skills)


def test_delete(faker, skill_repository):
    skill_name = faker.name()
    skill = skill_repository.add(Skill(name=skill_name))
    assert skill
    assert skill.name  # in the case of skills the name is the id

    skill_repository.delete(skill_name)
    skill = skill_repository.get_by_id(skill_name)
    assert not skill


def test_update(skill_repository):
    skill = skill_repository.add(Skill(name="python"))
    updated = skill_repository.update(skill.name, {"name": "rust"})

    assert updated
    assert updated.name == "rust"


def test_get_application_with_details(
    faker,
    company_repository,
    application_repository,
    skill_repository,
):
    company = company_repository.add(Company(name=faker.company()))
    skill = skill_repository.add(Skill(name=faker.name()))

    application = application_repository.add(
        Application(
            title=faker.job(),
            company_id=company.id,
            skills=[skill],
        )
    )

    application_with_details = application_repository.get_with_details(application.id)
    assert application_with_details
    assert application_with_details.company.name == company.name
    assert application_with_details.created_at
    assert application_with_details.last_updated
    assert hasattr(application_with_details, "skills")
    assert len(application_with_details.skills) == 1
    assert hasattr(application_with_details, "contacts")


def test_get_applications_by_status(faker, company_repository, application_repository):
    company = company_repository.add(Company(name=faker.company()))

    application_repository.add(
        Application(title="Job A", status=Status.APPLIED, company_id=company.id)
    )
    application_repository.add(
        Application(title="Job B", status=Status.INTERVIEWING, company_id=company.id)
    )

    applied_only = application_repository.get_by_status(Status.APPLIED)
    assert len(applied_only) == 1
    assert applied_only[0].title == "Job A"


def test_get_all_emails_from_contacts(contact_repository, faker):
    contacts_with_email = [
        Contact(name=faker.name(), email=faker.email()) for _ in range(10)
    ]
    for contact in contacts_with_email:
        contact_repository.add(contact)

    # add contact without email just in case
    contact_repository.add(Contact(name=faker.name()))

    emails = contact_repository.get_all_emails()
    assert emails
    assert len(emails) == len(contacts_with_email)

    for contact in contacts_with_email:
        assert contact.email in emails
