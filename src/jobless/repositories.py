from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from jobless.models import Application, Base, Company, Contact, Skill, Status

T = TypeVar("T", bound=Base)


class GenericRepository(Generic[T]):
    def __init__(self, model: type[T], session: Session):
        self.model = model
        self.session = session

    def add(self, instance: T) -> T:
        self.session.add(instance)
        self.session.flush()
        return instance

    def get_by_id(self, id: int | str) -> T | None:
        return self.session.get(self.model, id)

    def get_by_ids(self, ids: list[int | str]) -> list[T]:
        if not ids:
            return []

        statement = select(self.model).where(self.model.id.in_(ids))
        return list(self.session.scalars(statement).all())

    def get_with_details(self, id: int | str) -> T | None:
        raise NotImplementedError

    def get_all(self) -> list[T]:
        items = self.session.scalars(select(self.model)).all()
        return list(items)

    def update(self, instance: T) -> T:
        updated_instance = self.session.merge(instance)
        self.session.flush()
        return updated_instance

    def delete(self, id: int | str) -> None:
        item = self.get_by_id(id)
        if item:
            self.session.delete(item)
            self.session.flush()


class CompanyRepository(GenericRepository[Company]):
    def __init__(self, session: Session):
        super().__init__(Company, session)

    def get_with_details(self, id: int | str) -> Company | None:
        statement = (
            select(Company)
            .where(Company.id == id)
            .options(
                selectinload(Company.applications),
                selectinload(Company.contacts),
            )
        )
        result = self.session.scalars(statement).one_or_none()
        return result

    def get_by_name(self, name: str) -> Company | None:
        raise NotImplementedError

    def get_by_application(self, application_id: int) -> Company | None:
        statement = (
            select(Company)
            .join(Company.applications)
            .where(Application.id == application_id)
        )
        result = self.session.scalars(statement).first()
        return result

    def get_by_contact(self, contact_id: int) -> list[Company]:
        statement = (
            select(Company).join(Company.contacts).where(Contact.id == contact_id)
        )
        results = self.session.scalars(statement).all()
        return list(results)


class ApplicationRepository(GenericRepository[Application]):
    def __init__(self, session: Session):
        super().__init__(Application, session)

    def get_with_details(self, id: int | str) -> Application | None:
        statement = (
            select(Application)
            .where(Application.id == id)
            .options(
                joinedload(Application.company),
                selectinload(Application.skills),
                selectinload(Application.contacts),
            )
        )
        result = self.session.scalars(statement).one_or_none()
        return result

    def get_by_title(self, title: str) -> Application | None:
        raise NotImplementedError

    def get_by_company(self, company_id: int) -> list[Application]:
        statement = select(Application).where(Application.company_id == company_id)
        results = self.session.scalars(statement).all()
        return list(results)

    def get_by_skill(self, skill: str) -> list[Application]:
        statement = (
            select(Application).join(Application.skills).where(Skill.name == skill)
        )
        results = self.session.scalars(statement).all()
        return list(results)

    def get_by_contact(self, contact_id: int) -> list[Application]:
        statement = (
            select(Application)
            .join(Application.contacts)
            .where(Contact.id == contact_id)
        )
        results = self.session.scalars(statement).all()
        return list(results)

    def get_by_status(self, status: Status) -> list[Application]:
        statement = select(Application).where(Application.status == status)
        results = self.session.scalars(statement).all()
        return list(results)

    def get_by_priority(self, priority: int) -> list[Application]:
        statement = select(Application).where(Application.priority == priority)
        results = self.session.scalars(statement).all()
        return list(results)


class SkillRepository(GenericRepository[Skill]):
    def __init__(self, session: Session):
        super().__init__(Skill, session)

    def get_with_details(self, id: int | str) -> Skill | None:
        statement = (
            select(Skill)
            .where(Skill.name == id)
            .options(
                selectinload(Skill.applications),
            )
        )
        result = self.session.scalars(statement).one_or_none()
        return result

    def get_by_name(self, name: str) -> Skill | None:
        return self.get_by_id(name)

    def get_by_application(self, application_id: int) -> list[Skill]:
        statement = (
            select(Skill)
            .join(Skill.applications)
            .where(Application.id == application_id)
        )
        results = self.session.scalars(statement).all()
        return list(results)


class ContactRepository(GenericRepository[Contact]):
    def __init__(self, session: Session):
        super().__init__(Contact, session)

    def get_with_details(self, id: int | str) -> Contact | None:
        statement = (
            select(Contact)
            .where(Contact.name == id)
            .options(
                selectinload(Contact.applications),
                selectinload(Contact.companies),
            )
        )
        result = self.session.scalars(statement).one_or_none()
        return result

    def get_by_name(self, name: str) -> Contact | None:
        raise NotImplementedError

    def get_by_company(self, company_id: int) -> list[Contact]:
        statement = (
            select(Contact).join(Contact.companies).where(Company.id == company_id)
        )
        results = self.session.scalars(statement).all()
        return list(results)

    def get_by_application(self, application_id: int) -> list[Contact]:
        statement = (
            select(Contact)
            .join(Contact.applications)
            .where(Application.id == application_id)
        )
        results = self.session.scalars(statement).all()
        return list(results)

    def get_all_emails(self) -> list[str | None]:
        statement = select(Contact.email).where(Contact.email.is_not(None))
        results = self.session.scalars(statement).all()
        return list(results)
