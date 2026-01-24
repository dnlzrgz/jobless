from datetime import date
from typing import Generic, Type, TypeVar

from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable

from jobless.models import Application, Base, Company, Contact

T = TypeVar("T", bound=Base)


class JoblessTable(DataTable, Generic[T]):
    MODEL: Type[T]
    COLUMNS: list[str]
    LABEL: str
    PLURAL: str | None = None

    BINDINGS = [
        Binding(
            "backspace,delete",
            "delete",
            description="delete",
        ),
        Binding(
            "n",
            "new",
            description="new contact",
        ),
    ] + DataTable.BINDINGS

    class Delete(Message):
        def __init__(
            self,
            id: int,
            name: str,
        ) -> None:
            self.id = id
            self.name = name

            super().__init__()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.border_title = self.PLURAL or f"{self.LABEL}s"
        self.cursor_type = "row"
        self.zebra_stripes = True

    def on_mount(self) -> None:
        self.add_columns(*self.COLUMNS)

    def format_date(self, dt: date | None = None) -> str:
        return dt.strftime("%Y-%m-%d") if dt else "N/A"

    def item_to_row(self, item: T) -> tuple:
        raise NotImplementedError

    def reload(self, rows: list[tuple]) -> None:
        self.clear()
        self.add_rows(rows)
        self.border_subtitle = f"{len(rows)}"

        self.loading = False

    def action_delete(self) -> None:
        if self.cursor_row is not None:
            row_data = self.get_row_at(self.cursor_row)
            item_id = int(row_data[0])
            item_name = str(row_data[1])

            self.post_message(self.Delete(item_id, item_name))


class CompanyTable(JoblessTable):
    MODEL = Company
    COLUMNS = [
        "id",
        "name",
        "website",
        "industry",
        "applications",
        "contacts",
        "skills",
    ]
    LABEL = "company"
    PLURAL = "companies"

    class Delete(JoblessTable.Delete):
        pass

    def item_to_row(self, item: Company) -> tuple:
        return (
            str(item.id),
            item.name,
            item.website if item.website else "N/A",
            item.industry if item.industry else "N/A",
            str(len(item.applications)),
            str(len(item.contacts)),
            ", ".join(skill.name for skill in item.skills),
        )


class ApplicationTable(JoblessTable):
    MODEL = Application
    COLUMNS = [
        "id",
        "title",
        "company",
        "status",
        "priority",
        "contacts",
        "skills",
        "applied at",
        "last update at",
    ]
    LABEL = "application"

    class Delete(JoblessTable.Delete):
        pass

    def item_to_row(self, item: Application) -> tuple:
        return (
            str(item.id),
            item.title,
            item.company.name,
            item.status,
            str(item.priority),
            str(len(item.contacts)),
            ", ".join(skill.name for skill in item.skills),
            self.format_date(item.date_applied),
            self.format_date(item.follow_up_date),
        )


class ContactTable(JoblessTable):
    MODEL = Contact
    COLUMNS = [
        "id",
        "name",
        "email",
        "phone",
        "url",
        "companies",
        "applications",
    ]
    LABEL = "contact"

    class Delete(JoblessTable.Delete):
        pass

    def item_to_row(self, item: Contact) -> tuple:
        return (
            str(item.id),
            item.name,
            item.email if item.email else "N/A",
            item.phone if item.phone else "N/A",
            item.url if item.url else "N/A",
            str(len(item.companies)),
            str(len(item.applications)),
        )
