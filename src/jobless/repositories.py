from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload, sessionmaker

from jobless.models import Application, Base, Company, Contact, Skill, Status

T = TypeVar("T", bound=Base)


class GenericRepository(Generic[T]):
    def __init__(self, model: type[T], session_factory: sessionmaker):
        self.model = model
        self.session_factory = session_factory

    def add(self, instance: T) -> T:
        session = self.session_factory()
        try:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            session.expunge(instance)
            return instance
        finally:
            session.close()

    def get_by_id(self, id: int | str) -> T | None:
        session = self.session_factory()
        try:
            instance = session.get(self.model, id)
            if instance:
                session.expunge(instance)

            return instance
        finally:
            session.close()

    def get_by_ids(self, ids: list[int | str]) -> list[T]:
        if not ids:
            return []

        session = self.session_factory()
        try:
            statement = select(self.model).where(self.model.id.in_(ids))
            instances = list(session.scalars(statement).all())
            session.expunge_all()
            return instances
        finally:
            session.close()

    def get_with_details(self, id: int | str) -> T | None:
        raise NotImplementedError

    def get_all(self) -> list[T]:
        session = self.session_factory()
        try:
            instances = session.scalars(select(self.model)).all()
            session.expunge_all()
            return list(instances)
        finally:
            session.close()

    def update(self, id: int | str, data: dict) -> T | None:
        session = self.session_factory()
        try:
            instance = session.get(self.model, id)
            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)

                session.commit()
                session.refresh(instance)
                session.expunge(instance)

            return instance
        finally:
            session.close()

    def delete(self, id: int | str) -> None:
        session = self.session_factory()
        try:
            instance = self.get_by_id(id)
            if instance:
                session.delete(instance)
                session.commit()
        finally:
            session.close()


class CompanyRepository(GenericRepository[Company]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Company, session_factory)

    def get_with_details(self, id: int | str) -> Company | None:
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
                session.expunge(company)

            return company
        finally:
            session.close()

    def get_by_name(self, name: str) -> Company | None:
        raise NotImplementedError

    def get_by_application(self, application_id: int) -> Company | None:
        session = self.session_factory()
        try:
            statement = (
                select(Company)
                .join(Company.applications)
                .where(Application.id == application_id)
            )
            company = session.scalars(statement).first()
            if company:
                session.expunge(company)

            return company
        finally:
            session.close()

    def get_by_contact(self, contact_id: int) -> list[Company]:
        session = self.session_factory()
        try:
            statement = (
                select(Company).join(Company.contacts).where(Contact.id == contact_id)
            )
            companies = session.scalars(statement).all()
            session.expunge_all()
            return list(companies)
        finally:
            session.close()


class ApplicationRepository(GenericRepository[Application]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Application, session_factory)

    def get_with_details(self, id: int | str) -> Application | None:
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
            application = session.scalars(statement).one_or_none()
            if application:
                session.expunge(application)

            return application
        finally:
            session.close()

    def get_by_title(self, title: str) -> Application | None:
        raise NotImplementedError

    def _get_multiple(self, statement) -> list[Application]:
        session = self.session_factory()
        try:
            applications = list(session.scalars(statement).all())
            session.expunge_all()
            return applications
        finally:
            session.close()

    def get_by_company(self, company_id: int) -> list[Application]:
        statement = select(Application).where(Application.company_id == company_id)
        return self._get_multiple(statement)

    def get_by_skill(self, skill: str) -> list[Application]:
        statement = (
            select(Application).join(Application.skills).where(Skill.name == skill)
        )
        return self._get_multiple(statement)

    def get_by_contact(self, contact_id: int) -> list[Application]:
        statement = (
            select(Application)
            .join(Application.contacts)
            .where(Contact.id == contact_id)
        )
        return self._get_multiple(statement)

    def get_by_status(self, status: Status) -> list[Application]:
        statement = select(Application).where(Application.status == status)
        return self._get_multiple(statement)

    def get_by_priority(self, priority: int) -> list[Application]:
        statement = select(Application).where(Application.priority == priority)
        return self._get_multiple(statement)


class SkillRepository(GenericRepository[Skill]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Skill, session_factory)

    def get_with_details(self, id: int | str) -> Skill | None:
        session = self.session_factory()
        try:
            statement = (
                select(Skill)
                .where(Skill.name == id)
                .options(
                    selectinload(Skill.applications),
                )
            )
            skill = session.scalars(statement).one_or_none()
            if skill:
                session.expunge(skill)

            return skill
        finally:
            session.close()


class ContactRepository(GenericRepository[Contact]):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(Contact, session_factory)

    def get_with_details(self, id: int | str) -> Contact | None:
        session = self.session_factory()
        try:
            statement = (
                select(Contact)
                .where(Contact.name == id)
                .options(
                    selectinload(Contact.applications),
                    selectinload(Contact.companies),
                )
            )
            contact = session.scalars(statement).one_or_none()
            if contact:
                session.expunge(contact)

            return contact
        finally:
            session.close()

    def get_by_name(self, name: str) -> Contact | None:
        raise NotImplementedError

    def get_by_email(self, email: str) -> Contact | None:
        raise NotImplementedError

    def get_by_website(self, website: str) -> Contact | None:
        raise NotImplementedError

    def get_by_company(self, company_id: int) -> list[Contact]:
        session = self.session_factory()
        try:
            statement = (
                select(Contact).join(Contact.companies).where(Company.id == company_id)
            )
            contacts = session.scalars(statement).all()
            session.expunge_all()
            return list(contacts)
        finally:
            session.close()

    def get_by_application(self, application_id: int) -> list[Contact]:
        session = self.session_factory()
        try:
            statement = (
                select(Contact)
                .join(Contact.applications)
                .where(Application.id == application_id)
            )
            contacts = session.scalars(statement).all()
            session.expunge_all()
            return list(contacts)
        finally:
            session.close()

    def get_all_emails(self) -> list[str | None]:
        session = self.session_factory()
        try:
            statement = select(Contact.email).where(Contact.email.is_not(None))
            return list(session.scalars(statement).all())
        finally:
            session.close()
