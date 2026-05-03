from functools import lru_cache

from jobless import models, schemas


class Mapper:
    @staticmethod
    @lru_cache(maxsize=256)
    def _create_skill_schema(id: int, name: str) -> schemas.Skill:
        return schemas.Skill(id=id, name=name)

    @classmethod
    def skill_model_to_schema(cls, model: models.Skill) -> schemas.Skill:
        return cls._create_skill_schema(model.id, model.name)

    @staticmethod
    def skill_schema_to_model(schema: schemas.Skill) -> models.Skill:
        return models.Skill(id=schema.id, name=schema.name)

    @staticmethod
    def company_model_to_schema(model: models.Company) -> schemas.Company:
        return schemas.Company(
            id=model.id,
            name=model.name,
            url=model.url,
            industry=model.industry,
        )

    @staticmethod
    def company_schema_to_model(schema: schemas.Company) -> models.Company:
        return models.Company(
            id=schema.id,
            name=schema.name,
            url=schema.url,
            industry=schema.industry,
        )

    @staticmethod
    def contact_model_to_schema(model: models.Contact) -> schemas.Contact:
        return schemas.Contact(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            url=model.url,
        )

    @staticmethod
    def contact_schema_to_model(schema: schemas.Contact) -> models.Contact:
        return models.Contact(
            id=schema.id,
            name=schema.name,
            email=schema.email,
            phone=schema.phone,
            url=schema.url,
        )

    @classmethod
    def application_model_to_schema(
        cls,
        model: models.Application,
    ) -> schemas.Application:
        return schemas.Application(
            id=model.id,
            title=model.title,
            description=model.description,
            salary=model.salary,
            url=model.url,
            location_type=model.location_type,
            status=model.status,
            date_applied=model.date_applied,
            follow_up_date=model.follow_up_date,
            notes=model.notes,
            company=cls.company_model_to_schema(model.company),
            contacts=[cls.contact_model_to_schema(c) for c in model.contacts],
            skills=[cls.skill_model_to_schema(s) for s in model.skills],
        )

    @classmethod
    def application_schema_to_model(
        cls,
        schema: schemas.Application,
    ) -> models.Application:
        return models.Application(
            id=schema.id,
            title=schema.title,
            description=schema.description,
            salary=schema.salary,
            url=schema.url,
            location_type=schema.location_type,
            status=schema.status,
            date_applied=schema.date_applied,
            follow_up_date=schema.follow_up_date,
            notes=schema.notes,
            company=cls.company_schema_to_model(schema.company),
            contacts=[cls.contact_schema_to_model(c) for c in schema.contacts],
            skills=[cls.skill_schema_to_model(s) for s in schema.skills],
        )
