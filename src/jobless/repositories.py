from dataclasses import fields
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload, sessionmaker

from jobless.models import Application, Base, Company, Contact, Skill
from jobless.schemas import (
    ApplicationSchema,
    BaseSchema,
    CompanySchema,
    ContactSchema,
    LookupSchema,
    SkillSchema,
)

T = TypeVar("T", bound=Base)
S = TypeVar("S", bound=BaseSchema)


class GenericRepository(Generic[T, S]):
    def __init__(self, model: type[T], schema: type[S], session_factory: sessionmaker):
        self.model = model
        self.schema = schema
        self.session_factory = session_factory

    def _get_model_kwargs(self, schema: S) -> dict:
        model_kwargs = {}
        for f in fields(schema):
            if f.name == "id" or isinstance(getattr(schema, f.name), list):
                continue

            value = getattr(schema, f.name)
            if isinstance(value, BaseSchema):
                model_kwargs[f"{f.name}_id"] = value.id
            else:
                model_kwargs[f.name] = value

        return model_kwargs

    def add(self, schema: S) -> S:
        raise NotImplementedError

    def get_by_id(self, id: int) -> LookupSchema | None:
        session = self.session_factory()
        try:
            instance = session.get(self.model, id)
            if instance:
                return LookupSchema.from_model(instance)
        finally:
            session.close()

    def get_with_details(self, id: int) -> S | None:
        raise NotImplementedError

    def list(self) -> list[LookupSchema]:
        session = self.session_factory()
        try:
            instances = session.scalars(select(self.model)).all()
            return [LookupSchema.from_model(instance) for instance in instances]
        finally:
            session.close()

    def list_with_details(self) -> list[S]:
        raise NotImplementedError

    def _list_unique_values(self, column: Any) -> set[Any]:
        session = self.session_factory()
        try:
            statement = select(column).where(column.is_not(None))
            return set(session.scalars(statement).all())
        finally:
            session.close()

    def update(self, schema: S) -> S | None:
        raise NotImplementedError

    def delete(self, id: int) -> None:
        session = self.session_factory()
        try:
            instance = session.get(self.model, id)
            if instance:
                session.delete(instance)
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class CompanyRepository(GenericRepository[Company, CompanySchema]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Company, CompanySchema, session_factory)

    def add(self, schema: CompanySchema) -> CompanySchema:
        session = self.session_factory()
        try:
            company = Company(**self._get_model_kwargs(schema))

            if schema.contacts:
                ids = [contact.id for contact in schema.contacts]
                company.contacts = (
                    session.query(Contact).filter(Contact.id.in_(ids)).all()
                )

            session.add(company)
            session.commit()

            return CompanySchema.from_model(company)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_with_details(self, id: int) -> CompanySchema | None:
        session = self.session_factory()
        try:
            statement = (
                select(Company)
                .where(Company.id == id)
                .options(
                    selectinload(Company.applications),
                    selectinload(Company.contacts),
                )
            )
            company = session.scalars(statement).one_or_none()
            if company:
                return CompanySchema.from_model(company)
        finally:
            session.close()

    def list_with_details(self) -> list[CompanySchema]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Company.applications),
                    selectinload(Company.contacts),
                )
            ).all()

            return [CompanySchema.from_model(instance) for instance in instances]
        finally:
            session.close()

    def list_names(self) -> set[str]:
        return self._list_unique_values(Company.name)

    def list_urls(self) -> set[str]:
        return self._list_unique_values(Company.url)

    def update(self, schema: CompanySchema) -> CompanySchema | None:
        session = self.session_factory()
        try:
            instance = session.get(Company, schema.id)
            if not instance:
                return

            for key, value in self._get_model_kwargs(schema).items():
                setattr(instance, key, value)

            contact_ids = [contact.id for contact in schema.contacts]
            instance.contacts = (
                session.query(Contact).filter(Contact.id.in_(contact_ids)).all()
            )

            session.commit()
            return CompanySchema.from_model(instance)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class ApplicationRepository(GenericRepository[Application, ApplicationSchema]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Application, ApplicationSchema, session_factory)

    def add(self, schema: ApplicationSchema) -> ApplicationSchema:
        session = self.session_factory()
        try:
            application = Application(**self._get_model_kwargs(schema))

            if schema.skills:
                ids = [skill.id for skill in schema.skills]
                application.skills = (
                    session.query(Skill).filter(Skill.id.in_(ids)).all()
                )

            if schema.contacts:
                ids = [contact.id for contact in schema.contacts]
                application.contacts = (
                    session.query(Contact).filter(Contact.id.in_(ids)).all()
                )

            session.add(application)
            session.commit()

            return ApplicationSchema.from_model(application)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_with_details(self, id: int) -> ApplicationSchema | None:
        session = self.session_factory()
        try:
            statement = (
                select(Application)
                .where(Application.id == id)
                .options(
                    joinedload(Application.company),
                    selectinload(Application.skills),
                    selectinload(Application.contacts),
                )
            )
            instance = session.scalars(statement).one_or_none()
            if instance:
                return ApplicationSchema.from_model(instance)
        finally:
            session.close()

    def list_with_details(self) -> list[ApplicationSchema]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Application.company),
                    selectinload(Application.skills),
                    selectinload(Application.contacts),
                )
            ).all()

            return [ApplicationSchema.from_model(instance) for instance in instances]
        finally:
            session.close()

    def list_urls(self) -> set[str]:
        return self._list_unique_values(Application.url)

    def update(self, schema: ApplicationSchema) -> ApplicationSchema | None:
        session = self.session_factory()
        try:
            instance = session.get(Application, schema.id)
            if not instance:
                return

            for key, value in self._get_model_kwargs(schema).items():
                setattr(instance, key, value)

            skill_ids = [s.id for s in schema.skills]
            instance.skills = session.query(Skill).filter(Skill.id.in_(skill_ids)).all()

            contact_ids = [contact.id for contact in schema.contacts]
            instance.contacts = (
                session.query(Contact).filter(Contact.id.in_(contact_ids)).all()
            )

            session.commit()
            return ApplicationSchema.from_model(instance)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class SkillRepository(GenericRepository[Skill, SkillSchema]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Skill, SkillSchema, session_factory)

    def add(self, schema: SkillSchema) -> SkillSchema:
        session = self.session_factory()
        try:
            existing_skill = session.scalar(
                select(Skill).where(Skill.name == schema.name)
            )
            if existing_skill:
                return SkillSchema.from_model(existing_skill)

            new_skill = Skill(name=schema.name)

            if schema.applications:
                ids = [application.id for application in schema.applications]
                new_skill.applications = (
                    session.query(Application).filter(Application.id.in_(ids)).all()
                )

            session.add(new_skill)
            session.commit()

            return SkillSchema.from_model(new_skill)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_with_details(self, id: int) -> SkillSchema | None:
        session = self.session_factory()
        try:
            statement = (
                select(Skill)
                .where(Skill.id == id)
                .options(
                    selectinload(Skill.applications),
                )
            )
            instance = session.scalars(statement).one_or_none()
            if instance:
                return SkillSchema.from_model(instance)
        finally:
            session.close()

    def list_with_details(self) -> list[SkillSchema]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Skill.applications),
                )
            ).all()

            return [SkillSchema.from_model(instance) for instance in instances]
        finally:
            session.close()


class ContactRepository(GenericRepository[Contact, ContactSchema]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Contact, ContactSchema, session_factory)

    def add(self, schema: ContactSchema) -> ContactSchema:
        session = self.session_factory()
        try:
            contact = Contact(**self._get_model_kwargs(schema))

            if schema.companies:
                ids = [company.id for company in schema.companies]
                contact.companies = (
                    session.query(Company).filter(Company.id.in_(ids)).all()
                )

            if schema.applications:
                ids = [application.id for application in schema.applications]
                contact.applications = (
                    session.query(Application).filter(Application.id.in_(ids)).all()
                )

            session.add(contact)
            session.commit()

            return ContactSchema.from_model(contact)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_with_details(self, id: int) -> ContactSchema | None:
        session = self.session_factory()
        try:
            statement = (
                select(Contact)
                .where(Contact.id == id)
                .options(
                    selectinload(Contact.applications),
                    selectinload(Contact.companies),
                )
            )
            instance = session.scalars(statement).one_or_none()
            if instance:
                return ContactSchema.from_model(instance)
        finally:
            session.close()

    def list_with_details(self) -> list[ContactSchema]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Contact.applications),
                    selectinload(Contact.companies),
                )
            ).all()

            return [ContactSchema.from_model(instance) for instance in instances]
        finally:
            session.close()

    def list_emails(self) -> set[str]:
        return self._list_unique_values(Contact.email)

    def list_phones(self) -> set[str]:
        return self._list_unique_values(Contact.phone)

    def list_urls(self) -> set[str]:
        return self._list_unique_values(Contact.url)

    def update(self, schema: ContactSchema) -> ContactSchema | None:
        session = self.session_factory()
        try:
            instance = session.get(Contact, schema.id)
            if not instance:
                return

            for key, value in self._get_model_kwargs(schema).items():
                setattr(instance, key, value)

            company_ids = [company.id for company in schema.companies]
            instance.companies = (
                session.query(Company).filter(Company.id.in_(company_ids)).all()
            )

            application_ids = [application.id for application in schema.applications]
            instance.applications = (
                session.query(Application)
                .filter(Application.id.in_(application_ids))
                .all()
            )

            session.commit()
            return ContactSchema.from_model(instance)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
