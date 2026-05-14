import pytest
from sqlalchemy.exc import IntegrityError

from jobless import schemas
from jobless.enums import SkillSortField, SortOrder
from tests.factories import ApplicationFactory, ContactFactory, SkillFactory


def test_contact_add_adds_new_contact(contact_repo):
    result = contact_repo.add(ContactFactory.build(name="John"))
    assert result.id is not None
    assert result.name == "John"


def test_contact_get_returns_existing_contact(contact_repo):
    contact = ContactFactory(name="John")
    result = contact_repo.get(contact.id)
    assert contact.id == result.id


def test_contact_update_name(contact_repo):
    original = ContactFactory(name="John")
    updated = contact_repo.update(schemas.Contact(id=original.id, name="John Doe"))
    assert updated.id == original.id
    assert updated.name == "John Doe"


def test_contact_update_email(contact_repo):
    original = ContactFactory()
    new_email = "new@email.com"

    updated = contact_repo.update(
        schemas.Contact(id=original.id, name=original.name, email=new_email)
    )
    assert updated.email == new_email


def test_contact_update_duplicated_email(contact_repo):
    ContactFactory(name="John", email="john@doe.com")
    original = contact_repo.add(schemas.Contact(name="Bob", email="bob@example.com"))

    with pytest.raises(IntegrityError):
        contact_repo.update(
            schemas.Contact(
                id=original.id,
                name="Bob",
                email="john@doe.com",
            ),
        )


def test_contact_list_return_all_existing_contacts(contact_repo):
    ContactFactory.create_batch(6)
    assert len(contact_repo.list()) == 6


def test_contact_delete(contact_repo):
    contact = ContactFactory()
    contact_id = contact.id
    assert contact_repo.get(contact_id)

    contact_repo.delete(contact_id)
    assert contact_repo.get(contact_id) is None


def test_contact_filter_by_name(contact_repo):
    ContactFactory(name="John")
    ContactFactory(name="Bob")

    results = contact_repo.filter(schemas.ContactFilter(name="jo"))

    assert len(results) == 1
    assert results[0].name == "John"


def test_contact_filter_min_applications(contact_repo):
    busy = ContactFactory()
    quiet = ContactFactory()

    ApplicationFactory.create_batch(3, contacts=[busy])

    results = contact_repo.filter(schemas.ContactFilter(min_applications=3))
    ids = [r.id for r in results]

    assert busy.id in ids
    assert quiet.id not in ids


def test_contact_filter_max_applications(contact_repo):
    busy = ContactFactory()
    quiet = ContactFactory()

    ApplicationFactory.create_batch(3, contacts=[busy])

    results = contact_repo.filter(schemas.ContactFilter(max_applications=0))
    ids = [r.id for r in results]

    assert quiet.id in ids
    assert busy.id not in ids


def test_contact_filter_limit(contact_repo):
    ContactFactory.create_batch(5)
    assert len(contact_repo.list()) == 5

    results = contact_repo.filter(schemas.ContactFilter(limit=3))
    assert len(results) == 3


def test_skill_get_or_create_creates_new_skill(skill_repo):
    result = skill_repo.get_or_create("Rust")
    assert result.id is not None
    assert result.name == "Rust"


def test_skill_get_or_create_returns_existing_skill(skill_repo):
    result1 = skill_repo.get_or_create("Rust")
    result2 = skill_repo.get_or_create("Rust")
    assert result1.id == result2.id


def test_skill_update_name(skill_repo):
    original = skill_repo.get_or_create("Rust")
    updated = skill_repo.update(schemas.Skill(id=original.id, name="rust"))
    assert updated.id == original.id
    assert updated.name == "rust"


def test_skill_update_duplicated_name(skill_repo):
    skill_repo.get_or_create("Python")
    original = skill_repo.get_or_create("Rust")

    with pytest.raises(IntegrityError):
        skill_repo.update(schemas.Skill(id=original.id, name="Python"))


def test_skill_list_return_all_existing_skills(skill_repo):
    SkillFactory.create_batch(6)
    assert len(skill_repo.list()) == 6


def test_skill_delete(skill_repo):
    skill = SkillFactory()
    skill_id = skill.id
    assert skill_repo.get(skill_id)

    skill_repo.delete(skill_id)
    assert skill_repo.get(skill_id) is None


def test_skill_filter_by_name(skill_repo):
    SkillFactory(name="Python")
    SkillFactory(name="Go")

    results = skill_repo.filter(schemas.SkillFilter(name="pyth"))

    assert len(results) == 1
    assert results[0].name == "Python"


def test_skill_filter_min_applications(skill_repo):
    busy = SkillFactory()
    quiet = SkillFactory()

    ApplicationFactory.create_batch(3, skills=[busy])

    results = skill_repo.filter(schemas.SkillFilter(min_applications=3))
    ids = [r.id for r in results]

    assert busy.id in ids
    assert quiet.id not in ids


def test_skill_filter_max_applications(skill_repo):
    busy = SkillFactory()
    quiet = SkillFactory()

    ApplicationFactory.create_batch(3, skills=[busy])

    results = skill_repo.filter(schemas.SkillFilter(max_applications=0))
    ids = [r.id for r in results]

    assert quiet.id in ids
    assert busy.id not in ids


def test_skill_filter_sort_by_name_asc(skill_repo):
    SkillFactory(name="Zebra")
    SkillFactory(name="Ant")

    results = skill_repo.filter(
        schemas.SkillFilter(sort_by=SkillSortField.NAME, sort_order=SortOrder.ASC)
    )
    names = [r.name for r in results]

    assert names == sorted(names)


def test_skill_filter_sort_by_name_desc(skill_repo):
    SkillFactory(name="Zebra")
    SkillFactory(name="Ant")

    results = skill_repo.filter(
        schemas.SkillFilter(sort_by=SkillSortField.NAME, sort_order=SortOrder.DESC)
    )
    names = [r.name for r in results]

    assert names == sorted(names, reverse=True)


def test_skill_filter_sort_by_application_count(skill_repo):
    popular = SkillFactory()
    _ = SkillFactory()

    ApplicationFactory.create_batch(3, skills=[popular])
    results = skill_repo.filter(
        schemas.SkillFilter(
            sort_by=SkillSortField.NUMBER_APPLICATIONS, sort_order=SortOrder.DESC
        )
    )

    assert results[0].id == popular.id


def test_skill_filter_limit(skill_repo):
    SkillFactory.create_batch(5)
    assert len(skill_repo.list()) == 5

    results = skill_repo.filter(schemas.SkillFilter(limit=3))
    assert len(results) == 3
