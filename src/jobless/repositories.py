from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload, sessionmaker

from jobless.models import Application, Base, Company, Contact, Skill

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
        except Exception:
            session.rollback()
            raise
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

    def get_with_details(self, id: int | str) -> T | None:
        raise NotImplementedError

    def list(self) -> list[T]:
        session = self.session_factory()
        try:
            instances = session.scalars(select(self.model)).all()
            session.expunge_all()
            return list(instances)
        finally:
            session.close()

    def list_with_details(self) -> list[T]:
        raise NotImplementedError

    def _list_unique_values(self, column: Any) -> set[Any]:
        session = self.session_factory()
        try:
            statement = select(column).where(column.is_not(None))
            return set(session.scalars(statement).all())
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
        except Exception:
            session.rollback()
            raise
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

    def list_with_details(self) -> list[Company]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Company.applications),
                    selectinload(Company.contacts),
                )
            ).all()
            session.expunge_all()
            return list(instances)
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

    def list_names(self) -> set[str]:
        return self._list_unique_values(Company.name)

    def list_urls(self) -> set[str]:
        return self._list_unique_values(Company.url)


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

    def list_with_details(self) -> list[Application]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Application.company),
                    selectinload(Application.skills),
                    selectinload(Application.contacts),
                )
            ).all()
            session.expunge_all()
            return list(instances)
        finally:
            session.close()

    def list_urls(self) -> set[str]:
        return self._list_unique_values(Application.url)


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

    def list_with_details(self) -> list[Skill]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Skill.applications),
                )
            ).all()
            session.expunge_all()
            return list(instances)
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

    def list_with_details(self) -> list[Contact]:
        session = self.session_factory()
        try:
            instances = session.scalars(
                select(self.model).options(
                    selectinload(Contact.applications),
                    selectinload(Contact.companies),
                )
            ).all()
            session.expunge_all()
            return list(instances)
        finally:
            session.close()

    def list_emails(self) -> set[str]:
        return self._list_unique_values(Contact.email)

    def list_phones(self) -> set[str]:
        return self._list_unique_values(Contact.phone)

    def list_urls(self) -> set[str]:
        return self._list_unique_values(Contact.url)
