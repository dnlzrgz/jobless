import pytest
from jobless.mapper import Mapper
from tests.factories import (
    make_application_model,
    make_company_model,
    make_contact_model,
    make_skill_model,
)


@pytest.mark.parametrize(
    "factory, model_to_schema_fn, schema_to_model_fn",
    [
        (make_skill_model, Mapper.skill_model_to_schema, Mapper.skill_schema_to_model),
        (
            make_contact_model,
            Mapper.contact_model_to_schema,
            Mapper.contact_schema_to_model,
        ),
        (
            make_company_model,
            Mapper.company_model_to_schema,
            Mapper.company_schema_to_model,
        ),
    ],
)
def test_mapper_symmetry(
    factory,
    model_to_schema_fn,
    schema_to_model_fn,
):
    model = factory()

    # Check model to schema
    schema = model_to_schema_fn(model)
    assert schema.id == model.id
    assert schema.name == model.name

    # Check schema back to model
    model_back = schema_to_model_fn(schema)
    assert model_back.id == schema.id
    assert model_back.name == schema.name


def test_application_deep_mapping():
    model = make_application_model()
    schema = Mapper.application_model_to_schema(model)

    assert schema.id == model.id
    assert schema.title == model.title
    assert schema.status == model.status
    assert schema.location_type == model.location_type

    assert schema.company.id == model.company.id
    assert schema.company.name == model.company.name

    assert len(schema.skills) == len(model.skills)
    assert len(schema.contacts) == len(model.contacts)


def test_mapper_skill_caching():
    model = make_skill_model()

    schema1 = Mapper.skill_model_to_schema(model)
    schema2 = Mapper.skill_model_to_schema(model)

    assert schema1 is schema2
