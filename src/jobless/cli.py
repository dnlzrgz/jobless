import sys
from typing import Annotated, TextIO

import typer
from sqlalchemy.orm import sessionmaker

from jobless.commands import applications, companies, contacts, skills
from jobless.commands.utils import date_serializer
from jobless.context import AppContext
from jobless.db import get_engine
from jobless.mapper import Mapper
from jobless.settings import load_settings

cli = typer.Typer(
    help="Track and manage your job applications from the terminal.",
    no_args_is_help=True,
    suggest_commands=True,
)


@cli.callback()
def main(ctx: typer.Context):
    settings = load_settings()
    engine = get_engine(settings.db_url)

    ctx.obj = AppContext(
        session_factory=sessionmaker(
            bind=engine,
            expire_on_commit=False,
        ),
        mapper=Mapper(),
    )


@cli.command("export")
def export_all(
    ctx: typer.Context,
    output: Annotated[
        typer.FileTextWrite | None,
        typer.Option(
            "-o",
            "--output",
            help="file to write data to; defaults to stdout",
        ),
    ] = None,
    pretty: Annotated[
        bool,
        typer.Option(
            "--pretty/--compact",
            help="format json with identation or without",
        ),
    ] = True,
):
    """
    export data to json
    """

    context: AppContext = ctx.obj
    write_stream: TextIO = output if output is not None else sys.stdout
    with context.get_session() as session:
        import json
        from dataclasses import asdict

        from jobless.repositories import ApplicationRepository

        app_repo = ApplicationRepository(session, context.mapper)
        applications = app_repo.list()

        data = [asdict(a) for a in applications]
        json.dump(
            data,
            write_stream,
            default=date_serializer,
            indent=2 if pretty else None,
            ensure_ascii=False,
        )


cli.add_typer(applications.cli)
cli.add_typer(skills.cli)
cli.add_typer(companies.cli)
cli.add_typer(contacts.cli)


if __name__ == "__main__":
    cli()
