from sqlmodel import Session, select

from jobless.models import Contact


def add_contact(session: Session, contact: Contact) -> None:
    session.add(contact)


def get_contact(session: Session, contact_id: int) -> Contact | None:
    statement = select(Contact).where(Contact.id == contact_id)
    contact = session.exec(statement).one_or_none()
    return contact


def get_contact_by_email(session: Session, contact_email: str) -> Contact | None:
    statement = select(Contact).where(Contact.email == contact_email)
    contact = session.exec(statement).one_or_none()
    return contact


def get_contacts_by_name(session: Session, contact_name: str) -> list[Contact]:
    statement = select(Contact).where(Contact.name == contact_name)
    contacts = session.exec(statement).all()
    return list(contacts)


def get_all_contacts(session: Session) -> list[Contact]:
    contacts = session.exec(select(Contact)).all()
    return list(contacts)


def get_contacts_by_company(session: Session, company_id: int) -> list[Contact]:
    raise NotImplementedError


def get_contacts_by_application(session: Session, application_id: int) -> list[Contact]:
    raise NotImplementedError


def get_all_contact_emails(session: Session) -> list[str]:
    emails = session.exec(select(Contact.email)).all()
    return list(emails)


def delete_contact(session: Session, contact_id: int) -> None:
    statement = select(Contact).where(Contact.id == contact_id)
    contact = session.exec(statement).one_or_none()
    if not contact:
        return

    session.delete(contact)
