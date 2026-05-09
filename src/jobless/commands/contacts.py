from typing import Annotated

import typer

from jobless import schemas
from jobless.commands.utils import resolve_field
from jobless.context import AppContext
from jobless.repositories import ContactRepository

cli = typer.Typer(
    name="contact",
    help="manage contacts",
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
            help="contact name",
        ),
    ],
    email: Annotated[
        str | None,
        typer.Option(
            "-e",
            "--email",
            help="contact email",
        ),
    ] = None,
    phone: Annotated[
        str | None,
        typer.Option(
            "-p",
            "--phone",
            help="contact phone number",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="contact URL",
        ),
    ] = None,
):
    """
    Add a new contact.

    Examples:
      $ jobless contact add --name "Jane Smith" --email jane@acme.com
      $ jobless contact add -n "John Doe" --url https://linkedin.com/in/johndoe
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        contact_repo = ContactRepository(session, context.mapper)

        contact = schemas.Contact(
            name=name,
            email=email,
            phone=phone,
            url=url,
        )

        contact_repo.add(contact)
        session.commit()

        typer.echo("Contact added")


@cli.command("update")
def update(
    ctx: typer.Context,
    id: Annotated[
        int,
        typer.Argument(help="contact ID"),
    ],
    name: Annotated[
        str | None,
        typer.Option(
            "-n",
            "--name",
            help="new contact name",
        ),
    ] = None,
    email: Annotated[
        str | None,
        typer.Option(
            "-e",
            "--email",
            help="new contact email; use '' to clear",
        ),
    ] = None,
    phone: Annotated[
        str | None,
        typer.Option(
            "-p",
            "--phone",
            help="new contact phone; use '' to clear",
        ),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option(
            "-u",
            "--url",
            help="new contact url; use '' to clear",
        ),
    ] = None,
):
    """
    Update a contact.

    Only the fields you provide will be changed. To clear an optional field,
    pass an empty string.

    Examples:
      $ jobless contact update 2 --email newemail@acme.com
      $ jobless contact update 2 --phone ''
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        contact_repo = ContactRepository(session, context.mapper)

        existing = contact_repo.get(id)
        if not existing:
            typer.echo(f"contact {id} not found", err=True)
            raise typer.Exit(1)

        updated = schemas.Contact(
            id=existing.id,
            name=name if name is not None else existing.name,
            email=resolve_field(email, existing.email),
            phone=resolve_field(phone, existing.phone),
            url=resolve_field(url, existing.url),
        )

        contact_repo.update(updated)
        session.commit()

        typer.echo("Contact updated")


@cli.command("list")
def get_all(ctx: typer.Context):
    """
    List contacts with optional filters.
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        contact_repo = ContactRepository(session, context.mapper)
        contacts = contact_repo.list()

        if not contacts:
            typer.echo("No contacts found")
            return

        for contact in contacts:
            meta = "\t".join(filter(None, [contact.email, contact.phone, contact.url]))
            typer.echo(f"{contact.id}\t{contact.name}\t{meta}")


@cli.command("del")
def delete(
    ctx: typer.Context,
    contact_ids: Annotated[
        list[int],
        typer.Argument(help="ID(s) of contacts to delete"),
    ],
):
    """
    Delete one or more contacts.

    Examples:
      $ jobless contact del 2
      $ jobless contact del 2 6
    """
    context: AppContext = ctx.obj
    with context.get_session() as session:
        contact_repo = ContactRepository(session, context.mapper)

        valid = []
        for contact_id in contact_ids:
            contact = contact_repo.get(contact_id)
            if contact:
                valid.append(contact)
            else:
                typer.echo(f"contact {contact_id} not found, skipping", err=True)

        if not valid:
            raise typer.Exit(1)

        for contact in valid:
            contact_repo.delete(contact.id)

        session.commit()
        typer.echo(f"Deleted {len(valid)} contact(s)")
