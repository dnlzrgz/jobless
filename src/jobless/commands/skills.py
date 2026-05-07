from typing import Annotated
import typer

from jobless.context import AppContext
from jobless.repositories import SkillRepository

cli = typer.Typer(
    name="skill",
    help="view and remove skills",
    no_args_is_help=True,
    suggest_commands=True,
)


@cli.command("list")
def get_all(ctx: typer.Context):
    """
    List all skills.
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        skill_repo = SkillRepository(session, context.mapper)
        skills = skill_repo.list()

        if not skills:
            typer.echo("No skills found.")
            return

        for skill in skills:
            typer.echo(f"{skill.id}\t{skill.name}")


@cli.command("del")
def delete(
    ctx: typer.Context,
    skill_ids: Annotated[
        list[int],
        typer.Argument(help="skill ID(s) to delete"),
    ],
):
    """
    Delete one or more skills.

    Any applications linked to a deleted skill will have that skill removed.

    Examples:
        $ jobless skill del 2
        $ jobless skill del 2 5 9
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        skill_repo = SkillRepository(session, context.mapper)

        valid = []
        for id in skill_ids:
            skill = skill_repo.get(id)
            if skill:
                valid.append(skill)
            else:
                typer.echo(f"skill {id} not found, skipping", err=True)

        if not valid:
            raise typer.Exit(1)

        for skill in valid:
            skill_repo.delete(skill.id)

        session.commit()
        typer.echo(f"Deleted {len(valid)} skill(s)")
