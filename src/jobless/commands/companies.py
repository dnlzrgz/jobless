from typing import Annotated

import typer

from jobless import schemas
from jobless.commands.utils import resolve_field
from jobless.context import AppContext
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
            help="industry or sector",
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
        typer.echo(f"Added company '{name}'")


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
            prompt=True,
            help="company name",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="company website; pass '' to clear",
        ),
    ] = None,
    industry: Annotated[
        str | None,
        typer.Option(
            "-i",
            "--industry",
            help="industry or sector; pass '' to clear",
        ),
    ] = None,
):
    """
    Update a company.

    Only the fields provided will be changed. To clear an optional field,

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
def get_all(ctx: typer.Context):
    """
    List all companies.
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        company_repo = CompanyRepository(session, context.mapper)
        companies = company_repo.list()

        if not companies:
            typer.echo("No companies found")
            return

        for company in companies:
            meta = "\t".join(filter(None, [company.industry, company.url]))
            typer.echo(f"{company.id}\t{company.name}\t{meta}")


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
