from datetime import date, timedelta
from sqlalchemy.orm import sessionmaker

from jobless.db import get_engine, init_db
from jobless.models import Status
from jobless.repositories import (
    ApplicationRepository,
    SkillRepository,
)
from jobless.settings import Settings


def prune(days: int, dry_run: bool = False, confirm: bool = False) -> None:
    settings: Settings = Settings.load()
    engine = get_engine(settings.db_url)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    application_repository = ApplicationRepository(session_factory)
    skill_repository = SkillRepository(session_factory)

    cutoff_date = date.today() - timedelta(days=days)
    staled_applications = application_repository.list_stale(
        before_date=cutoff_date,
        statuses=[
            Status.REJECTED,
            Status.CLOSED,
            Status.GHOSTED,
            Status.WITHDRAWN,
        ],
    )
    if not staled_applications:
        print(f"🔍 no applications found older than {days} days ({cutoff_date})")
    else:
        print(f"🔍 found {len(staled_applications)} applications to prune")

    orphaned_skills = skill_repository.list_orphaned()
    if not orphaned_skills:
        print("🔍 no orphan skills found")
    else:
        print(f"🔍 found {len(orphaned_skills)} skills to prune")

    if not orphaned_skills and not staled_applications:
        return

    if dry_run:
        print("No records will be deleted!")
        for application in staled_applications:
            print(
                f"\t- [APPLICATION] {application.title} @ {application.company.label} ({application.status})"
            )

        for skill in orphaned_skills:
            print(f"\t- [SKILL] {skill.name})")

        return

    if not confirm:
        answer = input("⚠️ Are you sure you want to continue? [y/N]:")
        if answer.lower() != "y":
            print("aborted!")
            return

    print("🗑️ pruning records...")
    for application in staled_applications:
        assert application.id
        application_repository.delete(application.id)

    for skill in orphaned_skills:
        assert skill.id
        skill_repository.delete(skill.id)

    print("🧹 cleanup complete!")
