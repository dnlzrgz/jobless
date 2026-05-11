import pytest
from sqlalchemy.exc import IntegrityError

from jobless import schemas
from jobless.enums import SkillSortField, SortOrder
from tests.factories import ApplicationFactory, SkillFactory


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
    assert original.id

    updated = skill_repo.update(schemas.Skill(id=original.id, name="rust"))
    assert updated.id == original.id
    assert updated.name == "rust"


def test_skill_update_duplicated_name(skill_repo):
    skill_repo.get_or_create("Python")

    original = skill_repo.get_or_create("Rust")
    assert original.id

    with pytest.raises(IntegrityError):
        skill_repo.update(schemas.Skill(id=original.id, name="Python"))


def test_skill_list_return_all_existing_skills(skill_repo):
    SkillFactory.create_batch(6)
    assert len(skill_repo.list()) == 6


def test_skill_delete(skill_repo):
    skill = SkillFactory()
    assert skill_repo.get(skill.id)

    skill_repo.delete(skill.id)
    assert skill_repo.get(skill.id) is None


def test_skill_filter_by_name(skill_repo):
    SkillFactory(name="Python")
    SkillFactory(name="Go")

    results = skill_repo.filter(schemas.SkillFilter(name="pyth"))

    assert len(results) == 1
    assert results[0].name == "Python"


def test_skill_filter_by_name_case_insensitive(skill_repo):
    SkillFactory(name="Python")
    results = skill_repo.filter(schemas.SkillFilter(name="PYTH"))
    assert len(results) == 1


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
    results = skill_repo.filter(schemas.SkillFilter(limit=3))
    assert len(results) == 3
