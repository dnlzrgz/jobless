import sqlite3

import pytest
from faker import Faker

fake = Faker()


def test_company_creation(db_conn):
    cursor = db_conn.cursor()
    company_name = fake.company()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
    company_id = cursor.lastrowid

    company = cursor.execute(
        "SELECT * FROM companies WHERE name = ?", (company_name,)
    ).fetchone()

    assert company is not None
    assert company["id"] == company_id
    assert company["name"] == company_name


def test_unique_company_name_constraint(db_conn):
    cursor = db_conn.cursor()
    company_name = fake.company()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))


def test_application_creation(db_conn):
    cursor = db_conn.cursor()
    company_name = fake.company()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
    company_id = cursor.lastrowid

    job_title = fake.job()
    cursor.execute(
        "INSERT INTO applications (company_id, title, status) VALUES (?, ?, ?)",
        (company_id, job_title, "Applied"),
    )

    application = cursor.execute(
        "SELECT * FROM applications WHERE title = ?", (job_title,)
    ).fetchone()
    assert application is not None
    assert application["company_id"] == company_id
    assert application["status"] == "Applied"


def test_application_history_trigger_on_status_update(db_conn):
    cursor = db_conn.cursor()
    company_name = fake.company()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
    company_id = cursor.lastrowid

    # Create initial application with status 'Saved'.
    job_title = fake.job()
    status = "Saved"
    cursor.execute(
        "INSERT INTO applications (company_id, title, status) VALUES (?, ?, ?)",
        (company_id, job_title, status),
    )

    # Update status.
    new_status = "Applied"
    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, 1))

    # Check history table.
    history = cursor.execute(
        "SELECT * FROM application_history WHERE application_id = ?", (1,)
    ).fetchone()

    assert history is not None
    assert history["old_status"] == status
    assert history["new_status"] == new_status


def test_application_history_trigger_on_non_status_update(db_conn):
    cursor = db_conn.cursor()
    company_name = fake.company()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
    company_id = cursor.lastrowid

    # Create initial application with status 'Saved'.
    job_title = fake.job()
    status = "Saved"
    cursor.execute(
        "INSERT INTO applications (company_id, title, status) VALUES (?, ?, ?)",
        (company_id, job_title, status),
    )

    # Add notes.
    notes = fake.paragraph()
    cursor.execute("UPDATE applications SET notes = ? WHERE id = ?", (notes, 1))

    # Check history table.
    history = cursor.execute(
        "SELECT * FROM application_history WHERE application_id = ?", (1,)
    ).fetchone()

    assert history is None


def test_skill_creation(db_conn):
    cursor = db_conn.cursor()
    skill_name = fake.word()
    cursor.execute("INSERT INTO skills (name) VALUES (?)", (skill_name,))
    skill_id = cursor.lastrowid

    skill = cursor.execute(
        "SELECT * FROM skills WHERE name = ?", (skill_name,)
    ).fetchone()

    assert skill is not None
    assert skill["id"] == skill_id
    assert skill["name"] == skill_name


def test_contact_creation(db_conn):
    cursor = db_conn.cursor()
    name = fake.name()
    email = fake.email()
    phone = fake.phone_number()
    url = fake.url()

    cursor.execute(
        "INSERT INTO contacts (name, email, phone, url) VALUES (?, ?, ?, ?)",
        (name, email, phone, url),
    )
    contact_id = cursor.lastrowid

    contact = cursor.execute(
        "SELECT * FROM contacts WHERE name = ? AND email = ?", (name, email)
    ).fetchone()

    assert contact is not None
    assert contact["id"] == contact_id
    assert contact["name"] == name
    assert contact["email"] == email
    assert contact["phone"] == phone
    assert contact["url"] == url


def test_contact_application_relationship(db_conn):
    cursor = db_conn.cursor()

    # Setup parent records.
    company_name = fake.company()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
    company_id = cursor.lastrowid

    job_title = fake.job()
    cursor.execute(
        "INSERT INTO applications (company_id, title) VALUES (?, ?)",
        (company_id, job_title),
    )
    application_id = cursor.lastrowid

    contact_name = fake.name()
    cursor.execute(
        "INSERT INTO contacts (name) VALUES (?)",
        (contact_name,),
    )
    contact_id = cursor.lastrowid

    # Create record in junction table.
    cursor.execute(
        "INSERT INTO applications_contacts (contact_id, application_id) VALUES (?, ?)",
        (contact_id, application_id),
    )

    # Verify.
    result = cursor.execute(
        """
    SELECT contacts.name, applications.title
    FROM contacts
    JOIN applications_contacts ON contacts.id = applications_contacts.contact_id
    JOIN applications ON applications_contacts.application_id = applications.id
    WHERE applications.id = ?
    """,
        (application_id,),
    ).fetchone()

    assert result["name"] == contact_name
    assert result["title"] == job_title


def test_company_skill_relationship(db_conn):
    cursor = db_conn.cursor()

    # Setup parent records.
    company_name = fake.company()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
    company_id = cursor.lastrowid

    skill_name = "Python"
    cursor.execute("INSERT INTO skills (name) VALUES (?)", (skill_name,))
    skill_id = cursor.lastrowid

    # Create record in junction table.
    cursor.execute(
        "INSERT INTO companies_skills (company_id, skill_id) VALUES (?, ?)",
        (company_id, skill_id),
    )

    # Verify.
    result = cursor.execute(
        """
        SELECT
            c.name AS company_name,
            s.name AS skill_name
        FROM companies AS c
        JOIN companies_skills AS cs ON c.id = cs.company_id
        JOIN skills AS s ON cs.skill_id = s.id
        WHERE c.id = ?
    """,
        (company_id,),
    ).fetchone()

    assert result["company_name"] == company_name
    assert result["skill_name"] == skill_name
