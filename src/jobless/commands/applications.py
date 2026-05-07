from datetime import datetime
from typing import Annotated

import typer

from jobless import schemas
from jobless.commands.utils import resolve_field
from jobless.context import AppContext
from jobless.enums import Location, Status
from jobless.repositories import (
    ApplicationRepository,
    CompanyRepository,
    SkillRepository,
)

cli = typer.Typer(
    name="app",
    help="manage job applications",
    no_args_is_help=True,
    suggest_commands=True,
)


@cli.command("add")
def create(
    ctx: typer.Context,
    title: Annotated[
        str,
        typer.Option(
            "-t",
            "--title",
            prompt=True,
            help="job title or position name",
        ),
    ],
    company: Annotated[
        str,
        typer.Option(
            "-c",
            "--company",
            prompt=True,
            help="company name",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "-d",
            "--description",
            help="job description",
        ),
    ] = None,
    salary: Annotated[
        str | None,
        typer.Option(
            "--salary",
            help="salary or range (e.g. '50k-70k')",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="URL of the job posting",
        ),
    ] = None,
    location_type: Annotated[
        Location,
        typer.Option(
            "--location-type",
            help="work arrangement",
        ),
    ] = Location.ON_SITE,
    status: Annotated[
        Status,
        typer.Option(
            "--status",
            help="application status",
        ),
    ] = Status.SAVED,
    date_applied: Annotated[
        datetime | None,
        typer.Option(
            "--date-applied",
            help="date the application was submitted (YYYY-MM-DD)",
        ),
    ] = None,
    notes: Annotated[
        str | None,
        typer.Option(
            "--notes",
            help="additional notes or reminders",
        ),
    ] = None,
    skills: Annotated[
        list[str] | None,
        typer.Option(
            "--skill",
            help="required or related skill; can be specified multiple times",
        ),
    ] = None,
):
    """
    Add a new job application.

    Examples:
      $ jobless app add --title "Backend Engineer" --company Acme
      $ jobless app add -t "SRE" -c Initech --status applied --skill Python --skill Go
    """
    context: AppContext = ctx.obj
    with context.get_session() as session:
        app_repo = ApplicationRepository(session, context.mapper)
        company_repo = CompanyRepository(session, context.mapper)
        skill_repo = SkillRepository(session, context.mapper)

        target_company = company_repo.get_or_create(company)
        skill_schemas = []
        if skills:
            skill_schemas = [skill_repo.get_or_create(s) for s in skills]

        application = schemas.Application(
            title=title,
            company=target_company,
            description=description,
            salary=salary,
            url=url,
            location_type=location_type,
            status=status,
            date_applied=date_applied,
            notes=notes,
            skills=skill_schemas,
            contacts=[],  # TODO:
        )

        app_repo.add(application)
        session.commit()


@cli.command("update")
def update(
    ctx: typer.Context,
    id: Annotated[
        int,
        typer.Argument(help="application ID"),
    ],
    title: Annotated[
        str | None,
        typer.Option(
            "-t",
            "--title",
            help="job title or position name",
        ),
    ] = None,
    company: Annotated[
        str | None,
        typer.Option(
            "-c",
            "--company",
            help="company name",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "-d",
            "--description",
            help="job description; pass '' to clear",
        ),
    ] = None,
    salary: Annotated[
        str | None,
        typer.Option(
            "--salary",
            help="salary or range (e.g. '50k-70k'); pass '' to clear",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="URL of the job posting; pass '' to clear",
        ),
    ] = None,
    location_type: Annotated[
        Location | None,
        typer.Option(
            "--location-type",
            help="work arrangement",
        ),
    ] = None,
    status: Annotated[
        Status | None,
        typer.Option(
            "--status",
            help="application status",
        ),
    ] = None,
    date_applied: Annotated[
        datetime | None,
        typer.Option(
            "--date-applied",
            help="date the application was submitted (YYYY-MM-DD).",
        ),
    ] = None,
    notes: Annotated[
        str | None,
        typer.Option(
            "--notes",
            help="additional notes or reminders; pass '' to clear",
        ),
    ] = None,
    skills: Annotated[
        list[str] | None,
        typer.Option(
            "--skill",
            help="replace all skills: pass '' to clear",
        ),
    ] = None,
):
    """
    Update an existing job application.

    Only the fields provided will be changed. To clear an optional field,
    pass an empty string.

    Examples:
      $ jobless app update 3 --status interviewing
      $ jobless app update 3 --skill Python --skill Rust
      $ jobless app update 3 --notes ''
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        app_repo = ApplicationRepository(session, context.mapper)

        existing_app = app_repo.get(id)
        if not existing_app:
            typer.echo(f"application '{id}' not found!", err=True)
            raise typer.Exit(1)

        target_company = existing_app.company
        if company is not None:
            company_repo = CompanyRepository(session, context.mapper)
            target_company = company_repo.get_or_create(company)

        target_skills = existing_app.skills
        if skills is not None:
            if skills == [""]:
                target_skills = []
            else:
                skill_repo = SkillRepository(session, context.mapper)
                target_skills = [skill_repo.get_or_create(s) for s in skills]

        updated_app = schemas.Application(
            id=existing_app.id,
            title=title if title is not None else existing_app.title,
            company=target_company,
            description=resolve_field(description, existing_app.description),
            salary=resolve_field(salary, existing_app.salary),
            url=resolve_field(url, existing_app.url),
            location_type=location_type
            if location_type is not None
            else existing_app.location_type,
            status=status if status is not None else existing_app.status,
            date_applied=resolve_field(date_applied, existing_app.date_applied),
            notes=resolve_field(notes, existing_app.notes),
            skills=target_skills,
            contacts=existing_app.contacts,
        )

        app_repo.update(updated_app)
        session.commit()
        typer.echo(f"Updated application {id}")


@cli.command("list")
def get_all(ctx: typer.Context):
    """
    List job applications.
    """
    context: AppContext = ctx.obj
    with context.get_session() as session:
        app_repo = ApplicationRepository(session, context.mapper)
        applications = app_repo.list()

        if not applications:
            typer.echo("No applications found")
            return

        for app in applications:
            typer.echo(f"{app.id}\t{app.title} @ {app.company.name}\t[{app.status}]")


@cli.command("del")
def delete(
    ctx: typer.Context,
    app_ids: Annotated[
        list[int],
        typer.Argument(help="application ID(s) to delete"),
    ],
):
    """
    Delete one or more job applications.

    Examples:
      $ jobless app del 4
      $ jobless app del 4 7 12
    """
    context: AppContext = ctx.obj
    with context.get_session() as session:
        app_repo = ApplicationRepository(session, context.mapper)

        valid_apps = []
        for id in app_ids:
            app = app_repo.get(id)
            if app:
                valid_apps.append(app)
            else:
                typer.echo(f"application {id} not found. skipping", err=True)

        if not valid_apps:
            raise typer.Exit(1)

        for app in valid_apps:
            app_repo.delete(app.id)

        session.commit()
        typer.echo(f"Deleted {len(valid_apps)} application(s)")
