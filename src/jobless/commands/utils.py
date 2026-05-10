import json
from dataclasses import asdict
from datetime import date, datetime

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from jobless import schemas
from jobless.enums import OutputFormat

console = Console()


def resolve_field(new, existing):
    """
    Return the correct value when updating an optional field.
    """
    if new is None:
        return existing

    if new == "":
        return None

    return new


def date_serializer(obj):
    """
    JSON serializer for objects that are serializable by default.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError(f"type {type(obj)} is not serializable")


def _fmt_date(d: date | None) -> str:
    return d.strftime("%Y-%m-%d") if d else "-"


def _or_dash(value: str | None) -> str:
    return value or "-"


def print_applications(apps: list[schemas.Application], format: OutputFormat):
    if format == OutputFormat.JSON:
        output = [asdict(app) for app in apps]
        console.print(
            json.dumps(
                output,
                indent=2,
                default=date_serializer,
                ensure_ascii=False,
            )
        )
        return

    if format == OutputFormat.TABLE:
        table = Table(box=None, header_style="bold")
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Company")
        table.add_column("Status")
        table.add_column("Applied", justify="right")
        table.add_column("Follow Up", justify="right")

        for app in apps:
            table.add_row(
                str(app.id),
                app.title,
                app.company.name,
                app.status.value,
                _fmt_date(app.date_applied),
                _fmt_date(app.follow_up_date),
            )
        console.print(table)
    else:
        for app in apps:
            line = Text.assemble(
                (f"{app.id},", "bold"),
                f" '{app.title}',",
                f" '{app.company.name}',",
                f" {app.status.value.capitalize()},",
                f" {_fmt_date(app.date_applied)},",
                f" {_fmt_date(app.follow_up_date)}",
            )
            console.print(line)


def print_application(app: schemas.Application) -> None:
    tags = [f"[bold]{app.status.value}[/]", app.location_type.value]
    if app.salary:
        tags.append(app.salary)

    meta = Text.from_markup(" · ".join(tags))

    dates = []
    if app.date_applied:
        dates.append(f"applied {_fmt_date(app.date_applied)}")

    if app.follow_up_date:
        dates.append(f"follow-up {_fmt_date(app.follow_up_date)}")

    if dates:
        meta.append("\n" + " · ".join(dates))

    if app.skills:
        meta.append(
            "\n" + ", ".join(f"#{s.name}" for s in app.skills),
            style="italic",
        )
    if app.url:
        meta.append(f"\n{app.url}")

    title = Text.assemble(
        (app.title, "bold"),
        " @ ",
        (app.company.name, "bold"),
    )
    console.print(
        Panel(
            meta,
            title=title,
            title_align="left",
            padding=1,
        ),
    )

    if app.description:
        console.print(
            Panel(
                app.description,
                title="Description",
                title_align="left",
                padding=1,
            )
        )

    if app.notes:
        console.print(
            Panel(
                app.notes,
                title="Notes",
                title_align="left",
                padding=1,
            ),
        )

    cards = []

    company_parts = [(app.company.name, "bold")]
    if app.company.industry:
        company_parts.append((f"\n{app.company.industry}", ""))
    if app.company.url:
        company_parts.append((f"\n{app.company.url}", "dim"))

    cards.append(
        Panel(
            Text.assemble(*company_parts),
            title="Company",
            title_align="left",
            padding=1,
        )
    )

    if app.contacts:
        contact_text = Text()
        for i, c in enumerate(app.contacts):
            if i:
                contact_text.append("\n\n")

            contact_text.append(c.name, style="bold")
            if c.url:
                contact_text.append(f"\n{c.url}", style="dim")
            if c.email:
                contact_text.append(f"\n{c.email}", style="dim")
            if c.phone:
                contact_text.append(f"\n{c.phone}", style="dim")

        cards.append(
            Panel(
                contact_text,
                title="Contacts",
                title_align="left",
                padding=1,
            )
        )

    console.print(Columns(cards, expand=True))


def print_companies(companies: list[schemas.Company], format: OutputFormat):
    if format == OutputFormat.JSON:
        output = [asdict(company) for company in companies]
        console.print(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    if format == OutputFormat.TABLE:
        table = Table(box=None, header_style="bold")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Industry")
        table.add_column("URL")

        for company in companies:
            table.add_row(
                str(company.id),
                company.name,
                _or_dash(company.industry),
                _or_dash(company.url),
            )
        console.print(table)
    else:
        for company in companies:
            line = Text.assemble(
                (f"{company.id},", "bold"),
                f" {company.name},",
                f" {_or_dash(company.industry)},",
                f" {_or_dash(company.url)}",
            )
            console.print(line)


def print_company(company: schemas.Company) -> None:
    body_parts: list = [_or_dash(company.industry)]
    body_parts.append("\n" + _or_dash(company.url))
    console.print(
        Panel(
            Text.assemble(*body_parts),
            title=Text(company.name, style="bold"),
            title_align="left",
            padding=1,
        )
    )


def print_contacts(contacts: list[schemas.Contact], format: OutputFormat):
    if format == OutputFormat.JSON:
        output = [asdict(contact) for contact in contacts]
        console.print(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    if format == OutputFormat.TABLE:
        table = Table(box=None, header_style="bold")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Email")
        table.add_column("Phone")
        table.add_column("URL")

        for contact in contacts:
            table.add_row(
                str(contact.id),
                contact.name,
                _or_dash(contact.phone),
                _or_dash(contact.email),
                _or_dash(contact.url),
            )
        console.print(table)
    else:
        for contact in contacts:
            line = Text.assemble(
                (f"{contact.id},", "bold"),
                f" {contact.name},",
                f" {_or_dash(contact.phone)},",
                f" {_or_dash(contact.email)},",
                f" {_or_dash(contact.url)}",
            )
            console.print(line)


def print_contact(contact: schemas.Contact) -> None:
    body_parts: list = [(_or_dash(contact.email), "")]
    body_parts.append("\n" + _or_dash(contact.phone))
    body_parts.append("\n" + _or_dash(contact.url))
    console.print(
        Panel(
            Text.assemble(*body_parts),
            title=Text(contact.name, style="bold"),
            title_align="left",
            padding=1,
        )
    )
