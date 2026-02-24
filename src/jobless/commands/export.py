import csv
import io
import zipfile
from pathlib import Path

from sqlalchemy.orm import sessionmaker

from jobless.db import get_engine, init_db
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    ContactRepository,
)
from jobless.settings import Settings


def get_companies_data(session_factory: sessionmaker) -> tuple[list[str], list]:
    companies = CompanyRepository(session_factory).list_with_details()
    column_names = ["name", "url", "industry", "notes"]
    rows = [
        (
            item.name,
            item.url or "",
            item.industry or "",
            item.notes or "",
        )
        for item in companies
    ]

    return column_names, rows


def get_contacts_data(session_factory: sessionmaker) -> tuple[list[str], list]:
    contacts = ContactRepository(session_factory).list_with_details()
    column_names = ["name", "email", "phone", "url", "notes"]
    rows = [
        (
            item.name,
            item.email or "",
            item.phone or "",
            item.url or "",
            item.notes or "",
        )
        for item in contacts
    ]

    return column_names, rows


def get_applications_data(session_factory: sessionmaker) -> tuple[list[str], list]:
    applications = ApplicationRepository(session_factory).list_with_details()
    column_names = [
        "title",
        "description",
        "salary_range",
        "platform",
        "url",
        "address",
        "location_type",
        "status",
        "priority",
        "company",
        "date_applied",
        "follow_up_date",
        "notes",
        "skills",
    ]
    rows = [
        (
            item.title,
            item.description or "",
            item.salary_range or "",
            item.platform or "",
            item.url or "",
            item.address or "",
            item.location_type,
            item.status,
            item.priority,
            item.company.label,
            item.date_applied.isoformat() if item.date_applied else "",
            item.follow_up_date.isoformat() if item.follow_up_date else "",
            item.notes or "",
            ", ".join([skill.label for skill in item.skills]),
        )
        for item in applications
    ]

    return column_names, rows


def write_csv_to_path(file_path: Path, cols: list[str], rows: list, label: str) -> None:
    if not rows:
        print(f"⚠️ no {label} found to export!")
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with file_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(cols)
            writer.writerows(rows)
        print(f"✅ {label} exported successfully to '{file_path.as_posix()}'!")
    except Exception as e:
        print(f"⚠️ unexpected error exporting {label}: {e}")


def create_zip_archive(
    file_path: Path, session_factory: sessionmaker, registry: dict
) -> None:
    try:
        with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, func in registry.items():
                cols, rows = func(session_factory)
                if not rows:
                    continue

                string_buffer = io.StringIO(newline="")
                writer = csv.writer(string_buffer, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(cols)
                writer.writerows(rows)

                zf.writestr(f"{name}.csv", string_buffer.getvalue())

            print(f"✅ all data exported successfully to ZIP '{file_path.as_posix()}'!")
    except Exception as e:
        print(f"⚠️ unexpected error creating zip: {e}")


def export(file_path: Path, scope: str) -> None:
    settings: Settings = Settings.load()
    engine = get_engine(settings.db_url)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    registry = {
        "companies": get_companies_data,
        "contacts": get_contacts_data,
        "applications": get_applications_data,
    }

    if scope == "all":
        create_zip_archive(file_path, session_factory, registry)
    elif scope in registry:
        cols, rows = registry[scope](session_factory)
        write_csv_to_path(file_path, cols, rows, scope)
