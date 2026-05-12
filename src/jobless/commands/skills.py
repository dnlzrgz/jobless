from typing import Annotated

import typer

from jobless import schemas
from jobless.commands.utils import print_skills
from jobless.context import AppContext
from jobless.enums import OutputFormat, SkillSortField, SortOrder
from jobless.repositories import SkillRepository

cli = typer.Typer(
    name="skill",
    help="manage skills",
    no_args_is_help=True,
    suggest_commands=True,
)


@cli.command("update")
def update(
    ctx: typer.Context,
    id: Annotated[
        int,
        typer.Argument(help="skill id"),
    ],
    name: Annotated[
        str,
        typer.Option(
            "-n",
            "--name",
            help="new skill name",
        ),
    ],
):
    """
    Update a skill.

    Examples:
      $ jobless skill update 2 --name 'python'
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        skill_repo = SkillRepository(session, context.mapper)

        existing = skill_repo.get(id)
        if not existing:
            typer.echo(f"skill {id} not found", err=True)
            raise typer.Exit(1)

        updated = schemas.Skill(id=existing.id, name=name)

        skill_repo.update(updated)
        session.commit()

        typer.echo("Skill updated")


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
    min_applications: Annotated[
        int | None,
        typer.Option(
            "--min-applications",
            min=0,
            help="filter skills with at least this many applications",
        ),
    ] = None,
    max_applications: Annotated[
        int | None,
        typer.Option(
            "--max-applications",
            min=0,
            help="filter skills with at most this many applications",
        ),
    ] = None,
    sort_by: Annotated[
        SkillSortField,
        typer.Option(
            "--sort-by",
            help="property to sort by",
        ),
    ] = SkillSortField.CREATED,
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
    List all skills with optional filters.

    Examples:
        $ jobless skill list
        $ jobless skill list --name 'python'
        $ jobless skill list --min-applications 5
    """

    # TODO: add option to filter by application::{title, id, etc.}

    context: AppContext = ctx.obj
    f = schemas.SkillFilter(
        name=name,
        min_applications=min_applications,
        max_applications=max_applications,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
    )
    with context.get_session() as session:
        skill_repo = SkillRepository(session, context.mapper)
        skills = skill_repo.filter(f)

        if not skills:
            typer.echo("No skills found", err=True)
            raise typer.Exit(1)

        print_skills(skills, format)


@cli.command("del")
def delete(
    ctx: typer.Context,
    skill_ids: Annotated[
        list[int],
        typer.Argument(help="skill id(s) to delete"),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "-f",
            "--force",
            help="skip confirmation prompt(s)",
        ),
    ] = False,
):
    """
    Delete one or more skills.

    Examples:
        $ jobless skill del 2
        $ jobless skill del 2 5 9
        $ jobless skill del 2 --force
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        skill_repo = SkillRepository(session, context.mapper)

        valid_skills = []
        for id in skill_ids:
            skill = skill_repo.get(id)
            if skill:
                valid_skills.append(skill)
            else:
                typer.echo(f"skill {id} not found, skipping", err=True)

        if not valid_skills:
            typer.echo("nothing to do")
            raise typer.Exit(1)

        for skill in valid_skills:
            if not force:
                if not typer.confirm(
                    f"You're going to delete skill '{skill.name}'. Continue?",
                    default=False,
                ):
                    continue

            skill_repo.delete(skill.id)
            typer.echo(f"Skill '{skill.name}' deleted")

        session.commit()
