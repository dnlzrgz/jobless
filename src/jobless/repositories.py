from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager, joinedload, selectinload

from jobless import models, schemas
from jobless.mapper import Mapper


class ApplicationRepository:
    def __init__(self, session: Session, mapper: Mapper) -> None:
        self._session = session
        self._mapper = mapper

    def _get(self, id: int) -> models.Application | None:
        return self._session.scalars(
            select(models.Application)
            .where(models.Application.id == id)
            .options(
                joinedload(models.Application.company),
                selectinload(models.Application.skills),
                selectinload(models.Application.contacts),
            )
        ).one_or_none()

    def add(self, schema: schemas.Application) -> schemas.Application:
        application = models.Application(
            title=schema.title,
            description=schema.description,
            salary=schema.salary,
            url=schema.url,
            location_type=schema.location_type,
            status=schema.status,
            date_applied=schema.date_applied,
            follow_up_date=schema.follow_up_date,
            notes=schema.notes,
            company_id=schema.company.id if schema.company else None,
        )

        if schema.skills:
            skill_ids = [s.id for s in schema.skills]
            application.skills = self._session.scalars(
                select(models.Skill).where(models.Skill.id.in_(skill_ids))
            ).all()

        if schema.contacts:
            contact_ids = [c.id for c in schema.contacts]
            application.contacts = self._session.scalars(
                select(models.Contact).where(models.Contact.id.in_(contact_ids))
            ).all()

        self._session.add(application)
        self._session.flush()
        return self._mapper.application_model_to_schema(application)

    def get(self, id: int) -> schemas.Application | None:
        instance = self._get(id)
        return self._mapper.application_model_to_schema(instance) if instance else None

    def filter(self, f: schemas.ApplicationFilter) -> list[schemas.Application]:
        stmt = select(models.Application).options(
            joinedload(models.Application.company),
            selectinload(models.Application.skills),
            selectinload(models.Application.contacts),
        )

        if f.title:
            stmt = stmt.where(models.Application.title.ilike(f"%{f.title}%"))

        if f.statuses:
            stmt = stmt.where(models.Application.status.in_(f.statuses))

        if f.location_types:
            stmt = stmt.where(models.Application.location_type.in_(f.location_types))

        if f.company_id:
            stmt = stmt.where(models.Application.company_id == f.company_id)
        elif f.company_name:
            stmt = (
                stmt.join(models.Application.company)
                .where(models.Company.name.ilike(f.company_name))
                .options(contains_eager(models.Application.company))
            )

        if f.applied_after:
            stmt = stmt.where(models.Application.date_applied >= f.applied_after)

        if f.applied_before:
            stmt = stmt.where(models.Application.date_applied <= f.applied_before)

        if f.follow_up_date_after:
            stmt = stmt.where(
                models.Application.follow_up_date >= f.follow_up_date_after
            )

        if f.follow_up_date_before:
            stmt = stmt.where(
                models.Application.follow_up_date <= f.follow_up_date_before
            )

        if f.skills:
            stmt = stmt.where(
                models.Application.skills.any(models.Skill.name.in_(f.skills))
            )

        stmt = stmt.order_by(models.Application.date_applied.desc())
        instances = self._session.scalars(stmt).unique().all()
        return [self._mapper.application_model_to_schema(i) for i in instances]

    def list(self) -> list[schemas.Application]:
        return self.filter(schemas.ApplicationFilter())

    def list_by_company(self, company_id: int) -> list[schemas.Application]:
        return self.filter(schemas.ApplicationFilter(company_id=company_id))

    def update(self, schema: schemas.Application) -> schemas.Application | None:
        assert schema.id

        instance = self._get(schema.id)
        if not instance:
            return None

        instance.title = schema.title
        instance.description = schema.description
        instance.salary = schema.salary
        instance.url = schema.url
        instance.location_type = schema.location_type
        instance.status = schema.status
        instance.date_applied = schema.date_applied
        instance.follow_up_date = schema.follow_up_date
        instance.notes = schema.notes
        instance.company_id = schema.company.id if schema.company else None

        instance.skills = (
            self._session.scalars(
                select(models.Skill).where(
                    models.Skill.id.in_([s.id for s in schema.skills])
                )
            ).all()
            if schema.skills
            else []
        )

        instance.contacts = (
            self._session.scalars(
                select(models.Contact).where(
                    models.Contact.id.in_([c.id for c in schema.contacts])
                )
            ).all()
            if schema.contacts
            else []
        )

        self._session.flush()
        return self._mapper.application_model_to_schema(instance)

    def delete(self, id: int) -> None:
        instance = self._session.get(models.Application, id)
        if instance:
            self._session.delete(instance)
            self._session.flush()


class CompanyRepository:
    def __init__(self, session: Session, mapper: Mapper) -> None:
        self._session = session
        self._mapper = mapper

    def _get(self, id: int) -> models.Company | None:
        return self._session.get(models.Company, id)

    def get_or_create(self, name: str) -> schemas.Company:
        instance = self._session.scalar(
            select(models.Company).where(models.Company.name == name)
        )
        if not instance:
            instance = models.Company(name=name)
            self._session.add(instance)
            self._session.flush()

        return self._mapper.company_model_to_schema(instance)

    def add(self, schema: schemas.Company) -> schemas.Company:
        company = self._mapper.company_schema_to_model(schema)
        self._session.add(company)

        self._session.flush()
        return self._mapper.company_model_to_schema(company)

    def get(self, id: int) -> schemas.Company | None:
        instance = self._get(id)
        return self._mapper.company_model_to_schema(instance) if instance else None

    def list(self) -> list[schemas.Company]:
        instances = self._session.scalars(select(models.Company)).all()
        return [self._mapper.company_model_to_schema(i) for i in instances]

    def update(self, schema: schemas.Company) -> schemas.Company | None:
        assert schema.id

        instance = self._get(schema.id)
        if not instance:
            return None

        instance.name = schema.name
        instance.url = schema.url
        instance.industry = schema.industry

        self._session.flush()
        return self._mapper.company_model_to_schema(instance)

    def delete(self, id: int) -> None:
        instance = self._get(id)
        if instance:
            self._session.delete(instance)
            self._session.flush()


class ContactRepository:
    def __init__(self, session: Session, mapper: Mapper) -> None:
        self._session = session
        self._mapper = mapper

    def _get(self, id: int) -> models.Contact | None:
        return self._session.get(models.Contact, id)

    def add(self, schema: schemas.Contact) -> schemas.Contact:
        contact = self._mapper.contact_schema_to_model(schema)
        self._session.add(contact)
        self._session.flush()
        return self._mapper.contact_model_to_schema(contact)

    def get(self, id: int) -> schemas.Contact | None:
        instance = self._get(id)
        return self._mapper.contact_model_to_schema(instance) if instance else None

    def list(self) -> list[schemas.Contact]:
        instances = self._session.scalars(select(models.Contact)).all()
        return [self._mapper.contact_model_to_schema(i) for i in instances]

    def update(self, schema: schemas.Contact) -> schemas.Contact | None:
        assert schema.id

        instance = self._get(schema.id)
        if not instance:
            return None

        instance.name = schema.name
        instance.email = schema.email
        instance.phone = schema.phone
        instance.url = schema.url

        self._session.flush()
        return self._mapper.contact_model_to_schema(instance)

    def delete(self, id: int) -> None:
        instance = self._get(id)
        if instance:
            self._session.delete(instance)
            self._session.flush()


class SkillRepository:
    def __init__(self, session: Session, mapper: Mapper) -> None:
        self._session = session
        self._mapper = mapper

    def get(self, id: int) -> models.Skill | None:
        return self._session.get(models.Skill, id)

    def get_or_create(self, name: str) -> schemas.Skill:
        instance = self._session.scalar(
            select(models.Skill).where(models.Skill.name == name)
        )
        if not instance:
            instance = models.Skill(name=name)
            self._session.add(instance)
            self._session.flush()

        return self._mapper.skill_model_to_schema(instance)

    def list(self) -> list[schemas.Skill]:
        instances = self._session.scalars(select(models.Skill)).all()
        return [self._mapper.skill_model_to_schema(i) for i in instances]

    def list_orphaned(self) -> list[schemas.Skill]:
        instances = self._session.scalars(
            select(models.Skill).where(~models.Skill.applications.any())
        ).all()
        return [self._mapper.skill_model_to_schema(i) for i in instances]

    def delete(self, id: int) -> None:
        instance = self._session.get(models.Skill, id)
        if instance:
            self._session.delete(instance)
            self._session.flush()
