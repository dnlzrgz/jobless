from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, contains_eager, joinedload, selectinload

from jobless import models, schemas
from jobless.enums import (
    ApplicationSortField,
    CompanySortField,
    ContactSortField,
    SkillSortField,
    SortOrder,
)
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

        match f.sort_by:
            case ApplicationSortField.TITLE:
                sort_col = models.Application.title
            case ApplicationSortField.COMPANY:
                stmt = stmt.join(models.Application.company)
                sort_col = models.Company.name
            case ApplicationSortField.STATUS:
                sort_col = models.Application.status
            case ApplicationSortField.LOCATION_TYPE:
                sort_col = models.Application.location_type
            case ApplicationSortField.FOLLOW_UP_DATE:
                sort_col = models.Application.follow_up_date
            case ApplicationSortField.CREATED:
                sort_col = models.Application.created_at
            case ApplicationSortField.UPDATED:
                sort_col = models.Application.last_updated
            case _:
                sort_col = models.Application.date_applied

        stmt = stmt.order_by(
            sort_col.desc() if f.sort_order == SortOrder.DESC else sort_col.asc()
        )

        if f.limit is not None:
            stmt = stmt.limit(f.limit)

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
        instance = self._get(id)
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

    def filter(self, f: schemas.CompanyFilter) -> list[schemas.Company]:
        app_count = func.count(models.Application.id).label("app_count")
        needs_count = (
            f.min_applications is not None
            or f.max_applications is not None
            or f.sort_by == CompanySortField.NUMBER_APPLICATIONS
        )

        stmt = select(models.Company)

        if needs_count:
            stmt = stmt.outerjoin(models.Company.applications).group_by(
                models.Company.id
            )

        if f.name:
            stmt = stmt.where(models.Company.name.ilike(f"%{f.name}%"))

        if f.url:
            stmt = stmt.where(models.Company.url.ilike(f"%{f.url}%"))

        if f.industry:
            stmt = stmt.where(models.Company.industry.ilike(f"%{f.industry}%"))

        having_clauses = []
        if f.min_applications is not None:
            having_clauses.append(app_count >= f.min_applications)
        if f.max_applications is not None:
            having_clauses.append(app_count <= f.max_applications)

        if having_clauses:
            stmt = stmt.having(and_(*having_clauses))

        match f.sort_by:
            case CompanySortField.NAME:
                sort_col = models.Company.name
            case CompanySortField.NUMBER_APPLICATIONS:
                sort_col = app_count
            case CompanySortField.CREATED:
                sort_col = models.Company.created_at
            case CompanySortField.UPDATED:
                sort_col = models.Company.last_updated

        stmt = stmt.order_by(
            sort_col.desc() if f.sort_order == SortOrder.DESC else sort_col.asc()
        )

        if f.limit is not None:
            stmt = stmt.limit(f.limit)

        instances = self._session.scalars(stmt).unique().all()
        return [self._mapper.company_model_to_schema(i) for i in instances]

    def list(self) -> list[schemas.Company]:
        return self.filter(schemas.CompanyFilter())

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

    def filter(self, f: schemas.ContactFilter) -> list[schemas.Contact]:
        app_count = func.count(models.Application.id).label("app_count")
        needs_count = (
            f.min_applications is not None
            or f.max_applications is not None
            or f.sort_by == ContactSortField.NUMBER_APPLICATIONS
        )

        stmt = select(models.Contact)

        if needs_count:
            stmt = stmt.outerjoin(models.Contact.applications).group_by(
                models.Contact.id
            )

        if f.name:
            stmt = stmt.where(models.Contact.name.ilike(f"%{f.name}%"))

        if f.url:
            stmt = stmt.where(models.Contact.url.ilike(f"%{f.url}%"))

        if f.email:
            stmt = stmt.where(models.Contact.email.ilike(f"%{f.email}%"))

        having_clauses = []
        if f.min_applications is not None:
            having_clauses.append(app_count >= f.min_applications)
        if f.max_applications is not None:
            having_clauses.append(app_count <= f.max_applications)

        if having_clauses:
            stmt = stmt.having(and_(*having_clauses))

        match f.sort_by:
            case ContactSortField.NAME:
                sort_col = models.Contact.name
            case ContactSortField.EMAIL:
                sort_col = models.Contact.email
            case ContactSortField.NUMBER_APPLICATIONS:
                sort_col = app_count
            case ContactSortField.CREATED:
                sort_col = models.Contact.created_at
            case ContactSortField.UPDATED:
                sort_col = models.Contact.last_updated

        stmt = stmt.order_by(
            sort_col.desc() if f.sort_order == SortOrder.DESC else sort_col.asc()
        )

        if f.limit is not None:
            stmt = stmt.limit(f.limit)

        instances = self._session.scalars(stmt).unique().all()
        return [self._mapper.contact_model_to_schema(i) for i in instances]

    def list(self) -> list[schemas.Contact]:
        return self.filter(schemas.ContactFilter())

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

    def _get(self, id: int) -> models.Skill | None:
        return self._session.get(models.Skill, id)

    def get(self, id: int) -> schemas.Skill | None:
        instance = self._get(id)
        return self._mapper.skill_model_to_schema(instance) if instance else None

    def get_or_create(self, name: str) -> schemas.Skill:
        instance = self._session.scalar(
            select(models.Skill).where(models.Skill.name == name)
        )
        if not instance:
            instance = models.Skill(name=name)
            self._session.add(instance)
            self._session.flush()

        return self._mapper.skill_model_to_schema(instance)

    def filter(self, f: schemas.SkillFilter) -> list[schemas.Skill]:
        app_count = func.count(models.Application.id).label("app_count")
        needs_count = (
            f.min_applications is not None
            or f.max_applications is not None
            or f.sort_by == SkillSortField.NUMBER_APPLICATIONS
        )

        stmt = select(models.Skill)

        if needs_count:
            stmt = stmt.outerjoin(models.Skill.applications).group_by(models.Skill.id)

        if f.name:
            stmt = stmt.where(models.Skill.name.ilike(f"%{f.name}%"))

        having_clauses = []
        if f.min_applications is not None:
            having_clauses.append(app_count >= f.min_applications)
        if f.max_applications is not None:
            having_clauses.append(app_count <= f.max_applications)

        if having_clauses:
            stmt = stmt.having(and_(*having_clauses))

        match f.sort_by:
            case SkillSortField.NAME:
                sort_col = models.Skill.name
            case SkillSortField.NUMBER_APPLICATIONS:
                sort_col = app_count
            case SkillSortField.CREATED:
                sort_col = models.Skill.created_at
            case SkillSortField.UPDATED:
                sort_col = models.Skill.last_updated

        stmt = stmt.order_by(
            sort_col.desc() if f.sort_order == SortOrder.DESC else sort_col.asc()
        )

        if f.limit is not None:
            stmt = stmt.limit(f.limit)

        instances = self._session.scalars(stmt).unique().all()
        return [self._mapper.skill_model_to_schema(i) for i in instances]

    def list(self) -> list[schemas.Skill]:
        return self.filter(schemas.SkillFilter())

    def update(self, schema: schemas.Skill) -> schemas.Skill | None:
        assert schema.id

        instance = self._get(schema.id)
        if not instance:
            return None

        instance.name = schema.name

        self._session.flush()
        return self._mapper.skill_model_to_schema(instance)

    def delete(self, id: int) -> None:
        instance = self._get(id)
        if instance:
            self._session.delete(instance)
            self._session.flush()
