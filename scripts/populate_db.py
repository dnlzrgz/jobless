import sys
import time
from random import choice, randint, sample

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from jobless.db import get_engine, init_db
from jobless.models import Application, Company, Contact, Location, Skill, Status
from jobless.settings import Settings

try:
    from faker import Faker
except ImportError:
    print("Error: 'faker' package not found.")
    print("This script requires development dependencies.")
    sys.exit(1)

fake = Faker()
tech_skills = {
    "Python",
    "Rust",
    "SQL",
    "Textual",
    "Docker",
    "AWS",
    "FastAPI",
    "React",
    "JavaScript",
    "CSS",
    "Tailwind CSS",
}
settings = Settings()


def is_empty(session: Session) -> bool:
    statement = select(func.count()).select_from(Company)
    count = session.scalar(statement)
    return count == 0


def seed_data():
    start_time = time.perf_counter()

    engine = get_engine(db_url=settings.db_url)
    init_db(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as session:
        if not is_empty(session):
            print(f"❌ The database at {settings.db_url} is not empty.")
            print("Please delete the database file or clear the tables before seeding.")
            sys.exit(1)

        print(f"✨ Starting seed process for: {settings.db_url}")

        print("🌱 Generating contacts...")
        contacts = [
            Contact(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                url=fake.url(),
                notes=fake.sentence() if randint(0, 1) else None,
            )
            for _ in range(randint(10, 50))
        ]
        session.add_all(contacts)

        print("🌱 Making up skills...")
        skills = [Skill(name=name) for name in tech_skills]
        session.add_all(skills)

        print("🌱 Building up companies...")
        companies = [
            Company(
                name=fake.unique.company(),
                website=fake.url(),
                industry=fake.bs(),
                notes=fake.sentence() if randint(0, 1) else None,
                skills=sample(skills, randint(2, 5)),
                contacts=sample(contacts, randint(1, 3)),
            )
            for _ in range(randint(10, 50))
        ]
        session.add_all(companies)

        print("🌱 Adding applications...")
        applications = [
            Application(
                title=fake.job(),
                description=fake.paragraph(),
                salary_range=f"${randint(20, 50)}k - ${randint(110, 200)}k",
                platform=choice(["LinkedIn", "Indeed", "Direct", "Referral"]),
                url=fake.url(),
                location_type=choice(list(Location)),
                status=choice(list(Status)),
                priority=randint(0, 4),
                date_applied=fake.date_between(start_date="-1y", end_date="today"),
                notes=fake.sentence() if randint(0, 1) else None,
                company=choice(companies),
                skills=sample(skills, randint(2, 5)),
                contacts=sample(contacts, randint(1, 3)),
            )
            for _ in range(randint(100, 200))
        ]

        session.add_all(applications)

        print("💾 Committing transaction...")
        session.commit()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"✅ Successfully seeded database in {elapsed_time:.4f} seconds.")


if __name__ == "__main__":
    seed_data()
