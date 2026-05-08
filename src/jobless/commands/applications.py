from datetime import datetime
from typing import Annotated

import typer

from jobless import schemas
from jobless.commands.utils import console, print_applications, resolve_field
from jobless.context import AppContext
from jobless.enums import (
    ApplicationSortField,
    Location,
    OutputFormat,
    SortOrder,
    Status,
)
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
            help="job title",
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
            help="salary range (e.g. '50k-70k')",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="job posting URL",
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
            help="submission date (YYYY-MM-DD)",
        ),
    ] = None,
    notes: Annotated[
        str | None,
        typer.Option(
            "--notes",
            help="additional notes",
        ),
    ] = None,
    skills: Annotated[
        list[str] | None,
        typer.Option(
            "--skill",
            help="add a skill; repeat to add multiple",
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
            help="new job title",
        ),
    ] = None,
    company: Annotated[
        str | None,
        typer.Option(
            "-c",
            "--company",
            help="new company name",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "-d",
            "--description",
            help="new description; use '' to clear",
        ),
    ] = None,
    salary: Annotated[
        str | None,
        typer.Option(
            "--salary",
            help="new salary range; use '' to clear",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="new URL; use '' to clear",
        ),
    ] = None,
    location_type: Annotated[
        Location | None,
        typer.Option(
            "--location-type",
            help="new work arrangement",
        ),
    ] = None,
    status: Annotated[
        Status | None,
        typer.Option(
            "--status",
            help="new application status",
        ),
    ] = None,
    date_applied: Annotated[
        datetime | None,
        typer.Option(
            "--date-applied",
            help="new submission date (YYYY-MM-DD).",
        ),
    ] = None,
    follow_up_date: Annotated[
        datetime | None,
        typer.Option(
            "--follow-up-date",
            help="new follow up date (YYYY-MM-DD).",
        ),
    ] = None,
    notes: Annotated[
        str | None,
        typer.Option(
            "--notes",
            help="new notes; use '' to clear",
        ),
    ] = None,
    skills: Annotated[
        list[str] | None,
        typer.Option(
            "--skill",
            help="replace all skills; use '' to clear",
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
            follow_up_date=resolve_field(follow_up_date, existing_app.follow_up_date),
            notes=resolve_field(notes, existing_app.notes),
            skills=target_skills,
            contacts=existing_app.contacts,
        )

        app_repo.update(updated_app)
        session.commit()
        typer.echo(f"Updated application {id}")


@cli.command("list")
def get_all(
    ctx: typer.Context,
    title: Annotated[
        str | None,
        typer.Option(
            "-t",
            "--title",
            help="filter by title",
        ),
    ] = None,
    statuses: Annotated[
        list[Status] | None,
        typer.Option(
            "--status",
            help="filter by status; repeat to match multiple",
        ),
    ] = None,
    locations: Annotated[
        list[Location] | None,
        typer.Option(
            "--location-type",
            help="filter by work arrangement; repeat to match mutliple",
        ),
    ] = None,
    company_name: Annotated[
        str | None,
        typer.Option(
            "--company-name",
            help="filter by company name",
        ),
    ] = None,
    company_id: Annotated[
        int | None,
        typer.Option(
            "--company-id",
            help="filter by company ID",
        ),
    ] = None,
    skills: Annotated[
        list[str] | None,
        typer.Option(
            "--skill",
            help="filter by skill; repeat to match multiple",
        ),
    ] = None,
    applied_after: Annotated[
        datetime | None,
        typer.Option(
            "--applied-after", help="filter by date submitted (on or after YYYY-MM-DD)"
        ),
    ] = None,
    applied_before: Annotated[
        datetime | None,
        typer.Option(
            "--applied-before",
            help="filter by date submitted (on or before YYYY-MM-DD)",
        ),
    ] = None,
    follow_up_after: Annotated[
        datetime | None,
        typer.Option(
            "--follow-up-after",
            help="filter by follow-up date (on or after YYYY-MM-DD)",
        ),
    ] = None,
    follow_up_before: Annotated[
        datetime | None,
        typer.Option(
            "--follow-up-before",
            help="filter by follow-up date (on or before YYYY-MM-DD)",
        ),
    ] = None,
    sort_by: Annotated[
        ApplicationSortField,
        typer.Option(
            "--sort-by",
            help="property to sort by",
        ),
    ] = ApplicationSortField.CREATED,
    sort_order: Annotated[
        SortOrder,
        typer.Option(
            "--order",
            help="sort order",
        ),
    ] = SortOrder.DESC,
    format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            help="output format",
        ),
    ] = OutputFormat.TABLE,
    limit: Annotated[
        int | None,
        typer.Option(
            "--limit",
            "-n",
            min=1,
            help="limit the number of results",
        ),
    ] = None,
):
    """
    List job applications with optional filters.

    Examples:
      $ jobless app list --status applied --status interviewing
      $ jobless app list --location-type remote --skill python
      $ jobless app list --applied-after 2024-01-01
    """

    context: AppContext = ctx.obj
    filter = schemas.ApplicationFilter(
        title=title,
        statuses=statuses or [],
        location_types=locations or [],
        skills=skills or [],
        company_name=company_name,
        company_id=company_id,
        applied_after=applied_after.date() if applied_after else None,
        applied_before=applied_before.date() if applied_before else None,
        follow_up_date_after=follow_up_after.date() if follow_up_after else None,
        follow_up_date_before=follow_up_before.date() if follow_up_before else None,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
    )
    with context.get_session() as session:
        app_repo = ApplicationRepository(session, context.mapper)
        applications = app_repo.filter(filter)

        if not applications:
            console.print("No applications found")
            return

        print_applications(applications, format)


@cli.command("del")
def delete(
    ctx: typer.Context,
    app_ids: Annotated[
        list[int],
        typer.Argument(help="ID(s) of applications to delete"),
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
