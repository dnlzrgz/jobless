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
        table.add_column("URL")
        table.add_column("Status")
        table.add_column("Applied", justify="right")
        table.add_column("Follow Up", justify="right")

        for app in apps:
            table.add_row(
                str(app.id),
                app.title,
                app.company.name,
                app.url,
                app.status.value,
                app.date_applied.strftime("%Y-%m-%d") if app.date_applied else "-",
                app.follow_up_date.strftime("%Y-%m-%d") if app.follow_up_date else "-",
            )
        console.print(table)
    else:
        for app in apps:
            console.print(
                f"[bold]{app.id}[/]  {app.title} @ {app.company.name} [dim]({app.status.value})[/]"
            )


def print_application(app: schemas.Application) -> None:
    meta = Text()

    tags = [f"[bold]{app.status.value}[/]", app.location_type.value]
    if app.salary:
        tags.append(app.salary)
    meta.append_text(Text.from_markup(" · ".join(tags)))

    dates = []
    if app.date_applied:
        dates.append(f"applied {app.date_applied.strftime('%Y-%m-%d')}")

    if app.follow_up_date:
        dates.append(f"follow-up {app.follow_up_date.strftime('%Y-%m-%d')}")

    if dates:
        meta.append("\n" + " · ".join(dates))

    if app.skills:
        skills = ", ".join(f"#{s.name}" for s in app.skills)
        meta.append(f"\n{skills}", style="italic")

    if app.url:
        meta.append(f"\n{app.url}")

    title = Text.assemble(
        (app.title, "bold"),
        (" @ "),
        (app.company.name, "bold"),
    )
    console.print(
        Panel(
            meta,
            title=title,
            title_align="left",
            padding=(1),
        )
    )

    if app.description:
        console.print(
            Panel(app.description, title="Description", title_align="left", padding=(1))
        )

    if app.notes:
        console.print(Panel(app.notes, title="Notes", title_align="left", padding=(1)))

    cards = []

    company_lines = [(app.company.name, "bold")]
    if app.company.industry:
        company_lines.append((f"\n{app.company.industry}", ""))
    if app.company.url:
        company_lines.append((f"\n\n{app.company.url}", ""))

    company_body = Text.assemble(*company_lines)
    cards.append(Panel(company_body, title="Company", title_align="left", padding=(1)))

    if app.contacts:
        lines = []
        for c in app.contacts:
            lines.append(f"[bold]{c.name}[/]")
            if c.email:
                lines.append(f"[dim]{c.email}[/]")
            if c.phone:
                lines.append(f"[dim]{c.phone}[/]")

        contacts_body = Text.from_markup("\n".join(lines))
        cards.append(
            Panel(contacts_body, title="Contacts", title_align="left", padding=(1))
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
                company.industry,
                company.url,
            )
        console.print(table)
    else:
        for company in companies:
            console.print(
                f"[bold]{company.id}[/] {company.name} [italic]{company.industry}[italic] [link]{company.url}[/]"
            )
