import json
from dataclasses import asdict
from datetime import date, datetime

from rich.console import Console
from rich.table import Table

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
        table.add_column("Status")
        table.add_column("Applied", justify="right")
        table.add_column("Follow Up", justify="right")

        for app in apps:
            table.add_row(
                str(app.id),
                app.title,
                app.company.name,
                app.status.value,
                app.date_applied.strftime("%Y-%m-%d") if app.date_applied else "-",
                app.follow_up_date.strftime("%Y-%m-%d") if app.follow_up_date else "-",
            )
        console.print(table)
    else:
        for app in apps:
            console.print(
                f"[bold]{app.id}[/bold]  {app.title} @ {app.company.name} [dim]({app.status.value})[/dim]"
            )
