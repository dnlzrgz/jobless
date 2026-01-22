from typing import Generic, TypeVar

from sqlmodel import Session, select

from jobless.models import Application, Base, Company, Contact, Skill

T = TypeVar("T", bound=Base)


class GenericRepository(Generic[T]):
    def __init__(self, model: type[T], session: Session):
        self.model = model
        self.session = session

    def add(self, instance: T) -> T:
        self.session.add(instance)
        self.session.flush()
        return instance

    def get_by_id(self, id: int) -> T | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        items = self.session.exec(select(self.model)).all()
        return list(items)

    def update(self, instance: T) -> T:
        self.add(instance)
        self.session.flush()
        return instance

    def delete(self, id: int) -> None:
        item = self.session.get(self.model, id)
        if not item:
            return

        self.session.delete(item)


class CompanyRepository(GenericRepository[Company]):
    def __init__(self, session: Session):
        super().__init__(Company, session)

    def get_by_name(self, name: str) -> Company | None:
        raise NotImplementedError

    def get_by_application(self, application_id: int) -> list[Company]:
        raise NotImplementedError

    def get_by_skill(self, skill_id: int) -> list[Company]:
        raise NotImplementedError

    def get_by_contact(self, contact_id: int) -> list[Company]:
        raise NotImplementedError


class ApplicationRepository(GenericRepository[Application]):
    def __init__(self, session: Session):
        super().__init__(Application, session)

    def get_by_title(self, title: str) -> Application | None:
        raise NotImplementedError

    def get_by_company(self, company_id: int) -> list[Application]:
        raise NotImplementedError

    def get_by_skill(self, skill_id: int) -> list[Application]:
        raise NotImplementedError

    def get_by_contact(self, contact_id: int) -> list[Application]:
        raise NotImplementedError

    def get_by_status(self, status: int) -> list[Application]:
        raise NotImplementedError

    def get_by_priority(self, status: int) -> list[Application]:
        raise NotImplementedError


class SkillRepository(GenericRepository[Skill]):
    def __init__(self, session: Session):
        super().__init__(Skill, session)

    def get_by_name(self, name: str) -> Skill | None:
        raise NotImplementedError

    def get_by_company(self, company_id: int) -> list[Skill]:
        raise NotImplementedError

    def get_by_application(self, application_id: int) -> list[Skill]:
        raise NotImplementedError


class ContactRepository(GenericRepository[Contact]):
    def __init__(self, session: Session):
        super().__init__(Contact, session)

    def get_by_name(self, name: str) -> Contact | None:
        raise NotImplementedError

    def get_by_company(self, company_id: int) -> list[Contact]:
        raise NotImplementedError

    def get_by_application(self, application_id: int) -> list[Contact]:
        raise NotImplementedError

    def get_all_emails(self) -> list[str]:
        raise NotImplementedError
