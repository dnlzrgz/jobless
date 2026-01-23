from faker import Faker

from jobless.models import Application, Company, Contact, Skill, Status
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    ContactRepository,
    SkillRepository,
)

fake = Faker()


def test_add_and_get_by_id(session):
    skill_repo = SkillRepository(session)
    skill_name = fake.word()
    new_skill = Skill(name=skill_name)

    skill_repo.add(new_skill)

    skill_in_db = skill_repo.get_by_id(skill_name)
    assert skill_in_db
    assert skill_in_db.name == skill_name


def test_get_all(session):
    skill_repo = SkillRepository(session)

    skills = [Skill(name=name) for name in {"Python", "JavaScript", "C", "TDD"}]
    for skill in skills:
        skill_repo.add(skill)

    skills_in_db = skill_repo.get_all()
    assert len(skills_in_db) == len(skills)


def test_update(session):
    skill_repo = SkillRepository(session)
    skill = Skill(name=fake.word())
    skill_repo.add(skill)

    skill.name = "Rust"
    updated = skill_repo.update(skill)

    assert updated.name == "Rust"


def test_delete(session):
    skill_repo = SkillRepository(session)
    skill = Skill(name="JavaScript")
    skill_repo.add(skill)

    skill_repo.delete("JavaScript")
    assert not skill_repo.get_by_id("JavaScript")


def test_get_application_with_details(session):
    company_repo = CompanyRepository(session)
    application_repo = ApplicationRepository(session)

    company = Company(name=fake.company())
    company_repo.add(company)

    application = Application(
        title=fake.job(),
        company_id=company.id,
    )
    application_repo.add(application)
    session.commit()

    detailed_application = application_repo.get_with_details(application.id)
    assert detailed_application
    assert detailed_application.company.name == company.name
    assert detailed_application.created_at
    assert detailed_application.last_updated
    assert hasattr(detailed_application, "skills")
    assert hasattr(detailed_application, "contacts")


def test_get_applications_by_status(session):
    company_repo = CompanyRepository(session)
    application_repo = ApplicationRepository(session)

    company = Company(name=fake.company())
    company_repo.add(company)

    application_repo.add(
        Application(title="Job A", status=Status.APPLIED, company_id=company.id)
    )
    application_repo.add(
        Application(title="Job B", status=Status.INTERVIEWING, company_id=company.id)
    )
    session.flush()

    applied_only = application_repo.get_by_status(Status.APPLIED)
    assert len(applied_only) == 1
    assert applied_only[0].title == "Job A"


def test_get_company_by_skill(session):
    company_repo = CompanyRepository(session)
    skill_repo = SkillRepository(session)

    skill = Skill(
        name="Python",
    )
    skill_repo.add(skill)

    company = Company(name=fake.company(), skills=[skill])
    company_repo.add(company)
    session.flush()

    results = company_repo.get_by_skill(skill.name)
    assert results
    assert len(results) == 1
    assert results[0].name == company.name


def test_get_all_emails_from_contacts(session):
    contact_repo = ContactRepository(session)
    contacts = [Contact(name=fake.name(), email=fake.email()) for _ in range(10)]
    for contact in contacts:
        contact_repo.add(contact)

    # contact without email
    contact_repo.add(Contact(name=fake.name()))

    emails = contact_repo.get_all_emails()
    assert emails
    assert len(emails) == len(contacts)

    for contact in contacts:
        assert contact.email in emails
