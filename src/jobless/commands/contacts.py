import webbrowser
from typing import Annotated

import typer

from jobless import schemas
from jobless.commands.utils import (
    print_contact,
    print_contacts,
    resolve_field,
)
from jobless.context import AppContext
from jobless.enums import ContactSortField, OutputFormat, SortOrder
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


@cli.command("view")
def view(
    ctx: typer.Context,
    contact_id: Annotated[
        int,
        typer.Argument(help="contact id"),
    ],
    web: Annotated[
        bool,
        typer.Option(
            "-w",
            "--web",
            help="open the contact website if any.",
        ),
    ] = False,
):
    """
    Show contact details.

    Examples:
      $ jobless contact view 3
      $ jobless contact view 3 --web
    """

    context: AppContext = ctx.obj
    with context.get_session() as session:
        contact_repo = ContactRepository(session, context.mapper)
        contact = contact_repo.get(contact_id)
        if not contact:
            typer.echo(f"contact {contact_id} not found.", err=True)
            raise typer.Exit(1)

        if web:
            if not contact.url:
                typer.echo(f"contact {contact_id} has no URL ", err=True)
                raise typer.Exit(1)
            else:
                webbrowser.open(contact.url)
                return

        print_contact(contact)


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
    email: Annotated[
        str | None,
        typer.Option(
            "-e",
            "--email",
            help="filter by email",
        ),
    ] = None,
    min_applications: Annotated[
        int | None,
        typer.Option(
            "--min-applications",
            min=0,
            help="filter contacts with at least this many applications",
        ),
    ] = None,
    max_applications: Annotated[
        int | None,
        typer.Option(
            "--max-applications",
            min=0,
            help="filter contacts with at most this many applications",
        ),
    ] = None,
    sort_by: Annotated[
        ContactSortField,
        typer.Option(
            "--sort-by",
            help="property to sort by",
        ),
    ] = ContactSortField.CREATED,
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
    List contacts with optional filters.

    Examples:
        $ jobless contact list
        $ jobless contact list --name 'sarah'
        $ jobless contact list --min-applications 2 --order asc
    """

    # TODO: add option to filter by application::{title, id, etc.}

    context: AppContext = ctx.obj
    f = schemas.ContactFilter(
        name=name,
        url=url,
        email=email,
        min_applications=min_applications,
        max_applications=max_applications,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
    )

    with context.get_session() as session:
        contact_repo = ContactRepository(session, context.mapper)
        contacts = contact_repo.filter(f)

        if not contacts:
            typer.echo("No contacts found", err=True)
            raise typer.Exit(1)

        print_contacts(contacts, format)


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
            typer.echo(f"Deleted '{contact.name}'")

        session.commit()
