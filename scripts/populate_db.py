import sys
import time
from random import choice, randint, sample

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from jobless.db import get_engine, init_db
from jobless.enums import Location, Status
from jobless.models import Application, Company, Contact, Skill
from jobless.settings import load_settings

try:
    from faker import Faker
except ImportError:
    print("error: 'faker' package not found.")
    print("This script requires development dependencies.")
    sys.exit(1)

fake = Faker()
settings = load_settings()

SKILLS = {
    "python",
    "rust",
    "go",
    "typescript",
    "sql",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "fastapi",
    "django",
    "react",
    "vue",
    "svelte",
    "javascript",
    "css",
    "tailwind css",
    "graphql",
    "postgres",
    "redis",
    "kafka",
    "textual",
}


def is_empty(session: Session) -> bool:
    statement = select(func.count()).select_from(Application)
    return session.scalar(statement) == 0


def seed_data():
    start_time = time.perf_counter()

    engine = get_engine(db_url=settings.db_url)
    init_db(engine)

    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        if not is_empty(session):
            print(f"⚠️ database {settings.db_url} is not empty!")
            sys.exit(1)

        print("🌱 adding skills...")
        skills = [Skill(name=name) for name in SKILLS]
        session.add_all(skills)
        session.flush()

        print("🌱 adding companies...")
        companies = [
            Company(
                name=fake.unique.company(),
                url=fake.unique.url(),
                industry=fake.bs(),
            )
            for _ in range(randint(10, 50))
        ]
        session.add_all(companies)
        session.flush()

        print("🌱 adding applications...")
        applications = []
        for _ in range(randint(100, 200)):
            applied_date = fake.date_between(start_date="-2y", end_date="today")
            updated_date = fake.date_between(start_date=applied_date, end_date="today")
            follow_up_date = (
                fake.date_between(start_date=applied_date, end_date="+30d")
                if randint(0, 1)
                else None
            )

            application = Application(
                title=fake.job(),
                description=fake.paragraph(),
                salary=f"${randint(20, 50)}k - ${randint(110, 200)}k",
                url=fake.unique.url(),
                location_type=choice(list(Location)),
                status=choice(list(Status)),
                date_applied=applied_date,
                follow_up_date=follow_up_date,
                last_updated=updated_date,
                company=choice(companies),
                skills=sample(skills, randint(2, 3)),
                contacts=[
                    Contact(
                        name=fake.name(),
                        email=fake.unique.email(),
                        phone=fake.unique.phone_number(),
                        url=fake.unique.url(),
                    )
                    for _ in range(randint(2, 3))
                ],
                notes=fake.paragraph(),
            )
            applications.append(application)

        session.add_all(applications)
        session.commit()

    print(f"✅ seeded in {time.perf_counter() - start_time:.2f}s")


if __name__ == "__main__":
    seed_data()
