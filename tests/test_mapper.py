from jobless import schemas
from tests import factories


def test_skill_model_to_schema(mapper):
    model = factories.SkillFactory.build()
    result = mapper.skill_model_to_schema(model)

    assert isinstance(result, schemas.Skill)
    assert result.id == model.id
    assert result.name == model.name


def test_skill_model_to_schema_roundtrip(mapper):
    original = factories.SkillFactory.build()
    result = mapper.skill_schema_to_model(mapper.skill_model_to_schema(original))

    assert result.id == original.id
    assert result.name == original.name


def test_company_model_to_schema(mapper):
    model = factories.CompanyFactory.build()
    result = mapper.company_model_to_schema(model)

    assert isinstance(result, schemas.Company)
    assert result.id == model.id
    assert result.name == model.name
    assert result.url == model.url
    assert result.industry == model.industry


def test_company_model_to_schema_roundtrip(mapper):
    original = factories.CompanyFactory.build()
    result = mapper.company_schema_to_model(mapper.company_model_to_schema(original))

    assert result.id == original.id
    assert result.name == original.name
    assert result.url == original.url
    assert result.industry == original.industry


def test_contact_model_to_schema(mapper):
    model = factories.ContactFactory.build()
    result = mapper.contact_model_to_schema(model)

    assert isinstance(result, schemas.Contact)
    assert result.id == model.id
    assert result.name == model.name
    assert result.url == model.url
    assert result.email == model.email
    assert result.phone == model.phone


def test_contact_model_to_schema_roundtrip(mapper):
    original = factories.ContactFactory.build()
    result = mapper.contact_schema_to_model(mapper.contact_model_to_schema(original))

    assert result.id == original.id
    assert result.name == original.name
    assert result.url == original.url
    assert result.email == original.email
    assert result.phone == original.phone


def test_application_model_to_schema(mapper):
    model = factories.ApplicationFactory.build()
    result = mapper.application_model_to_schema(model)

    assert isinstance(result, schemas.Application)
    assert result.id == model.id
    assert result.title == model.title
    assert result.status == model.status
    assert result.date_applied == model.date_applied
    assert result.follow_up_date == model.follow_up_date
    assert result.location_type == model.location_type
    assert result.company.name == model.company.name
    assert len(result.contacts) == len(model.contacts)
    assert len(result.skills) == len(model.skills)


def test_application_model_to_schema_roundtrip(mapper):
    original = factories.ApplicationFactory.build()
    result = mapper.application_schema_to_model(
        mapper.application_model_to_schema(original)
    )

    assert result.id == original.id
    assert result.title == original.title
    assert result.status == original.status
    assert result.date_applied == original.date_applied
    assert result.follow_up_date == original.follow_up_date
    assert result.location_type == original.location_type
    assert result.company.name == original.company.name
    assert len(result.contacts) == len(original.contacts)
    assert len(result.skills) == len(original.skills)
