from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from email_validator import validate_email, EmailNotValidError


class Base(DeclarativeBase):
    pass


class Status(StrEnum):
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"


class Location(StrEnum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"


application_skill_link = Table(
    "application_skill_link",
    Base.metadata,
    Column(
        "application_id",
        ForeignKey("applications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "skill_name",
        ForeignKey("skills.name", ondelete="CASCADE"),
        primary_key=True,
    ),
)

company_contact_link = Table(
    "company_contact_link",
    Base.metadata,
    Column(
        "company_id",
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "contact_id",
        ForeignKey("contacts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

application_contact_link = Table(
    "application_contact_link",
    Base.metadata,
    Column(
        "application_id",
        ForeignKey("applications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "contact_id",
        ForeignKey("contacts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)
    website: Mapped[str | None] = mapped_column(String, unique=True)
    industry: Mapped[str | None] = mapped_column(String)

    notes: Mapped[str | None] = mapped_column(String)

    applications: Mapped[list[Application]] = relationship(
        back_populates="company",
        cascade="all, delete",
    )
    contacts: Mapped[list[Contact]] = relationship(
        back_populates="companies",
        secondary=company_contact_link,
    )


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String)
    salary_range: Mapped[str | None] = mapped_column(String)

    platform: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)
    address: Mapped[str | None] = mapped_column(String)
    location_type: Mapped[Location | None] = mapped_column(String)
    status: Mapped[Status] = mapped_column(String, default=Status.SAVED, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    date_applied: Mapped[date | None] = mapped_column()
    follow_up_date: Mapped[date | None] = mapped_column()

    notes: Mapped[str | None] = mapped_column(String)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped[Company] = relationship(back_populates="applications")

    contacts: Mapped[list[Contact]] = relationship(
        back_populates="applications",
        secondary=application_contact_link,
    )
    skills: Mapped[list[Skill]] = relationship(
        back_populates="applications",
        secondary=application_skill_link,
    )


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String, primary_key=True)

    applications: Mapped[list[Application]] = relationship(
        back_populates="skills",
        secondary=application_skill_link,
    )


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str | None] = mapped_column(String, index=True, unique=True)
    phone: Mapped[str | None] = mapped_column(String, unique=True)
    url: Mapped[str | None] = mapped_column(String)

    notes: Mapped[str | None] = mapped_column(String)

    companies: Mapped[list[Company]] = relationship(
        back_populates="contacts",
        secondary=company_contact_link,
    )
    applications: Mapped[list[Application]] = relationship(
        back_populates="contacts",
        secondary=application_contact_link,
    )

    @validates("email")
    def validate_email(self, key, email):
        try:
            email_info = validate_email(email, check_deliverability=False)
            return email_info.normalized
        except EmailNotValidError as e:
            raise ValueError(f"failed email validation: {e}")
