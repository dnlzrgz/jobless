import sqlite3
from contextlib import contextmanager


def init_db(conn: sqlite3.Connection) -> None:
    """
    Initializes database schema, tables, indexes, and automated triggers.
    """

    cursor = conn.cursor()

    # Create companies table.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        website TEXT,
        industry TEXT,

        notes TEXT,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create applications table.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        salary_range TEXT,
        location_type TEXT CHECK(location_type IN ('Remote', 'Hybrid', 'On-site')),

        platform TEXT,
        url TEXT,

        priority INTEGER DEFAULT 0 CHECK(priority >= 0 AND priority <= 4),
        status TEXT DEFAULT 'Saved' CHECK(status IN ('Saved', 'Applied', 'Interviewing', 'Offer', 'Rejected', 'Ghosted')),
        date_applied DATE,
        follow_up_date DATE,
        notes TEXT,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );
    """)

    # Create table for application history.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS application_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT,
        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
    );
    """)

    # Create skills table.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # Create contacts table.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        url TEXT,

        notes TEXT,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create junction table for skills and companies.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies_skills (
        company_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        PRIMARY KEY (company_id, skill_id),
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
    );
    """)

    # Create junction table for skills and applications.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications_skills (
        application_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        PRIMARY KEY (application_id, skill_id),
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
    );
    """)

    # Create junction table for contacts and companies.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies_contacts (
        contact_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        PRIMARY KEY (contact_id, company_id),
        FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );
    """)

    # Create junction table for contacts and applications.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications_contacts(
        contact_id INTEGER NOT NULL,
        application_id INTEGER NOT NULL,
        PRIMARY KEY (contact_id, application_id),
        FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
    );
    """)

    # Triggers.
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_companies_timestamp
    AFTER UPDATE ON companies
    BEGIN
        UPDATE companies SET last_updated = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_applications_timestamp
    AFTER UPDATE ON applications
    BEGIN
        UPDATE applications SET last_updated = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_contacts_timestamp
    AFTER UPDATE ON contacts
    BEGIN
        UPDATE contacts SET last_updated = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """)

    # Only fires if the 'status' column of an application is actually changed.
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS log_status_change
    AFTER UPDATE OF status ON applications
    WHEN OLD.status <> NEW.status
    BEGIN
        INSERT INTO application_history (application_id, old_status, new_status)
        VALUES (OLD.id, OLD.status, NEW.status);
    END;
    """)


@contextmanager
def get_connection(db_url: str):
    conn = sqlite3.connect(db_url)

    conn.row_factory = sqlite3.Row  # Rows as dict.

    # TODO: check values.
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA mmap_size = 268435456;")  # 256mb
    conn.execute("PRAGMA journal_size_limit = 5242880;")  # 5mb
    conn.execute("PRAGMA cache_size = 2000;")
    conn.execute("PRAGMA temp_store = MEMORY;")

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
