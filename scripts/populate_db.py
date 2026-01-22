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
TECH_SKILLS = {
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
SETTINGS = Settings()


def is_empty(session: Session) -> bool:
    statement = select(func.count()).select_from(Company)
    return session.scalar(statement) == 0


def seed_data():
    start_time = time.perf_counter()

    engine = get_engine(db_url=SETTINGS.db_url)
    init_db(engine)

    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        if not is_empty(session):
            sys.exit(1)

        print(f"✨ Starting seed for: {SETTINGS.db_url}")

        print("🌱 Adding skills...")
        skills = [Skill(name=name) for name in TECH_SKILLS]
        session.add_all(skills)

        print("🌱 Adding contacts...")
        contacts = [
            Contact(
                name=fake.name(),
                email=fake.unique.email(),
                phone=fake.phone_number(),
                url=fake.url(),
            )
            for _ in range(randint(10, 50))
        ]
        session.add_all(contacts)
        session.flush()

        print("🌱 Adding companies...")
        companies = [
            Company(
                name=fake.unique.company(),
                website=fake.url(),
                industry=fake.bs(),
                skills=sample(skills, randint(2, 4)),
                contacts=sample(contacts, randint(1, 2)),
            )
            for _ in range(randint(10, 50))
        ]
        session.add_all(companies)
        session.flush()

        print("🌱 Adding applications...")
        applications = []
        for _ in range(randint(100, 200)):
            applied = fake.date_between(start_date="-1y", end_date="today")
            application = Application(
                title=fake.job(),
                description=fake.paragraph(),
                salary_range=f"${randint(20, 50)}k - ${randint(110, 200)}k",
                platform=choice(["LinkedIn", "Indeed", "Direct", "Referral"]),
                url=fake.url(),
                location_type=choice(list(Location)),
                status=choice(list(Status)),
                priority=randint(0, 4),
                date_applied=applied,
                follow_up_date=applied if randint(0, 1) else None,
                company=choice(companies),
                skills=sample(skills, randint(2, 3)),
                contacts=sample(contacts, 1),
            )
            applications.append(application)

        session.add_all(applications)

        print("💾 Finalizing transaction...")
        session.commit()

    print(f"✅ Seeded in {time.perf_counter() - start_time:.2f}s")


if __name__ == "__main__":
    seed_data()
