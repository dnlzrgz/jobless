import webbrowser
from typing import Annotated

import typer

from jobless import schemas
from jobless.commands.utils import print_companies, print_company, resolve_field
from jobless.context import AppContext
from jobless.enums import CompanySortField, OutputFormat, SortOrder
from jobless.repositories import ApplicationRepository, CompanyRepository

cli = typer.Typer(
    name="company",
    help="manage companies",
    no_args_is_help=True,
    suggest_commands=True,
)


@cli.command("add")
def create(
    ctx: typer.Context,
    name: Annotated[
        str,
        typer.Option(
            "-n",
            "--name",
            prompt=True,
            help="company name",
        ),
    ],
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="company website",
        ),
    ] = None,
    industry: Annotated[
        str | None,
        typer.Option(
            "-i",
            "--industry",
            help="industry",
        ),
    ] = None,
):
    """
    Add a new company.

    Examples:
      $ jobless company add --name Acme
      $ jobless company add -n Acme --industry "software" --url https://initech.com
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        company_repo = CompanyRepository(session, context.mapper)

        company = schemas.Company(name=name, url=url, industry=industry)

        company_repo.add(company)
        session.commit()

        typer.echo("Company added")


@cli.command("view")
def view(
    ctx: typer.Context,
    company_id: Annotated[
        int,
        typer.Argument(help="company id"),
    ],
    web: Annotated[
        bool | None,
        typer.Option(
            "-w",
            "--web",
            help="open the company website if any.",
        ),
    ] = None,
):
    """
    Show company details.

    Examples:
      $ jobless company view 3
      $ jobless company view 3 --web
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        company_repo = CompanyRepository(session, context.mapper)
        company = company_repo.get(company_id)
        if not company:
            typer.echo(f"company {id} not found.", err=True)
            raise typer.Exit(1)

        if web:
            if not company.url:
                typer.echo(f"company {id} has no URL ", err=True)
                raise typer.Exit(1)
            else:
                webbrowser.open(company.url)
                return

        print_company(company)


@cli.command("update")
def update(
    ctx: typer.Context,
    id: Annotated[
        int,
        typer.Argument(help="company ID"),
    ],
    name: Annotated[
        str | None,
        typer.Option(
            "-n",
            "--name",
            help="new company name",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="new company website; use '' to clear",
        ),
    ] = None,
    industry: Annotated[
        str | None,
        typer.Option(
            "-i",
            "--industry",
            help="industry; use '' to clear",
        ),
    ] = None,
):
    """
    Update an existing company.

    Only the fields provided will be changed. To clear an optional field

    Examples:
        $ jobless company update 1 --name "Acme Corp"
        $ jobless company update 1 --industry ''
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        company_repo = CompanyRepository(session, context.mapper)

        existing = company_repo.get(id)
        if not existing:
            typer.echo(f"company {id} not found", err=True)
            raise typer.Exit(1)

        updated = schemas.Company(
            id=existing.id,
            name=name if name is not None else existing.name,
            url=resolve_field(url, existing.url),
            industry=resolve_field(industry, existing.industry),
        )

        company_repo.update(updated)
        session.commit()

        typer.echo(f"Updated company {id}")


@cli.command("list")
def get_all(
    ctx: typer.Context,
    name: Annotated[
        str | None,
        typer.Option(
            "-n",
            "--name",
            help="filter by name",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="filter by url",
        ),
    ] = None,
    industry: Annotated[
        str | None,
        typer.Option(
            "-i",
            "--industry",
            help="filter by industry",
        ),
    ] = None,
    min_applications: Annotated[
        int | None,
        typer.Option(
            "--min-applications",
            min=0,
            help="filter companies with at least this many applications",
        ),
    ] = None,
    max_applications: Annotated[
        int | None,
        typer.Option(
            "--max-applications",
            min=0,
            help="filter companies with at most this many applications",
        ),
    ] = None,
    sort_by: Annotated[
        CompanySortField,
        typer.Option(
            "--sort-by",
            help="property to sort by",
        ),
    ] = CompanySortField.CREATED,
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
            min=1,
            help="limit the number of results",
        ),
    ] = None,
):
    """
    List all companies with optional filters.

    Examples:
        $ jobless companies list
        $ jobless companies list --industry 'fintech' --sort-by name
        $ jobless companies list --min-applications 2 --order asc
    """

    context: AppContext = ctx.obj
    f = schemas.CompanyFilter(
        name=name,
        url=url,
        industry=industry,
        min_applications=min_applications,
        max_applications=max_applications,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
    )
    with context.get_session() as session:
        company_repo = CompanyRepository(session, context.mapper)
        companies = company_repo.filter(f)

        if not companies:
            typer.echo("No companies found")
            return

        print_companies(companies, format)


@cli.command("del")
def delete(
    ctx: typer.Context,
    company_ids: Annotated[
        list[int],
        typer.Argument(help="company ID(s) to delete"),
    ],
):
    """
    Delete one or more companies.

    If a company has linked applications, you will be asked to confirm
    before they are removed alongside it.

    Examples:
      $ jobless company del 1
      $ jobless company del 1 3
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        company_repo = CompanyRepository(session, context.mapper)
        app_repo = ApplicationRepository(session, context.mapper)

        valid = []
        for company_id in company_ids:
            company = company_repo.get(company_id)
            if company:
                valid.append(company)
            else:
                typer.echo(f"company {company_id} not found, skipping", err=True)

        if not valid:
            raise typer.Exit(1)

        for company in valid:
            linked = app_repo.list_by_company(company.id)

            if linked:
                typer.echo(
                    f"'{company.name}' has {len(linked)} linked application(s): "
                    + ", ".join(str(a.id) for a in linked)
                )

                confirmed = typer.confirm(
                    "Delete the company and all linked applications?"
                )
                if not confirmed:
                    typer.echo(f"Skipping '{company.name}'")
                    continue

                for app in linked:
                    app_repo.delete(app.id)

            company_repo.delete(company.id)
            typer.echo(f"Deleted '{company.name}'")

        session.commit()
