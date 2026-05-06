import typer
from sqlalchemy.orm import sessionmaker

from jobless.commands import applications
from jobless.context import AppContext
from jobless.db import get_engine
from jobless.mapper import Mapper
from jobless.settings import load_settings

cli = typer.Typer(
    help="Track and manage your job applications from the terminal.",
    no_args_is_help=True,
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


cli.add_typer(
    applications.cli,
    name="apps",
    help="create, view, and manage job applications",
)

if __name__ == "__main__":
    cli()
