from datetime import date, datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Table, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from jobless.enums import Location, Status


class Base(DeclarativeBase):
    pass


application_skill_link = Table(
    "application_skill_link",
    Base.metadata,
    Column(
        "application_id",
        ForeignKey("applications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "skill_id",
        ForeignKey("skills.id", ondelete="CASCADE"),
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
    url: Mapped[str | None] = mapped_column(String, unique=True)
    industry: Mapped[str | None] = mapped_column(String)
    applications: Mapped[list[Application]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String,
        index=True,
        unique=True,
    )
    applications: Mapped[list[Application]] = relationship(
        secondary=application_skill_link,
        back_populates="skills",
    )


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    url: Mapped[str | None] = mapped_column(String, unique=True)
    email: Mapped[str | None] = mapped_column(String, unique=True)
    phone: Mapped[str | None] = mapped_column(String, unique=True)
    applications: Mapped[list["Application"]] = relationship(
        secondary=application_contact_link,
        back_populates="contacts",
    )


class Application(Base, TimestampMixin):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String)
    salary: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, unique=True)
    location_type: Mapped[Location] = mapped_column(
        Enum(Location),
        default=Location.ON_SITE,
    )
    status: Mapped[Status] = mapped_column(
        Enum(Status),
        default=Status.SAVED,
        index=True,
    )
    date_applied: Mapped[date | None] = mapped_column()
    follow_up_date: Mapped[date | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(String)
    company_id: Mapped[int] = mapped_column(
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        )
    )
    company: Mapped[Company] = relationship(back_populates="applications")
    contacts: Mapped[list[Contact]] = relationship(
        secondary=application_contact_link,
        back_populates="applications",
    )
    skills: Mapped[list[Skill]] = relationship(
        secondary=application_skill_link,
        back_populates="applications",
    )
