from datetime import date
from typing import Generic, Type, TypeVar

from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable

from jobless.schemas import ApplicationSchema, BaseSchema, CompanySchema, ContactSchema


S = TypeVar("S", bound=BaseSchema)


class JoblessTable(DataTable, Generic[S]):
    SCHEMA: Type[S]
    COLUMNS: list[str]

    BINDINGS = DataTable.BINDINGS + [
        Binding(
            "backspace,delete",
            "delete",
            description="delete",
        ),
        Binding(
            "e",
            "update",
            description="edit",
        ),
        Binding(
            "n",
            "create",
            description="new",
        ),
        Binding("up,k", "cursor_up", "cursor up", show=False),
        Binding("down,j", "cursor_down", "cursor down", show=False),
        Binding("right,l", "cursor_right", "cursor right", show=False),
        Binding("left,h", "cursor_left", "cursor left", show=False),
        Binding("g,ctrl+home", "scroll_top", "top", show=False),
        Binding("G,ctrl+end", "scroll_bottom", "bottom", show=False),
    ]

    class Create(Message):
        def __init__(self, table: JoblessTable) -> None:
            self.table = table
            super().__init__()

    class Update(Message):
        def __init__(self, table: JoblessTable, id: int) -> None:
            self.table = table
            self.id = id
            super().__init__()

    class Delete(Message):
        def __init__(self, table: JoblessTable, id: int) -> None:
            self.table = table
            self.id = id
            super().__init__()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True

    def on_mount(self) -> None:
        self.add_columns(*self.COLUMNS)

    def format_date(self, dt: date | None = None) -> str:
        return dt.strftime("%Y-%m-%d") if dt else "N/A"

    def item_to_row(self, item: S) -> tuple:
        raise NotImplementedError

    def _get_current_row_id(self) -> int | None:
        if self.cursor_row is not None:
            row_data = self.get_row_at(self.cursor_row)
            id = int(row_data[0])
            return id

    def reload(self, rows: list[tuple]) -> None:
        self.clear()
        self.add_rows(rows)
        self.border_subtitle = f"{len(rows)}"

    def action_create(self) -> None:
        self.post_message(self.Create(self))

    def action_update(self) -> None:
        if item_id := self._get_current_row_id():
            self.post_message(self.Update(self, item_id))

    def action_delete(self) -> None:
        if item_id := self._get_current_row_id():
            self.post_message(self.Delete(self, item_id))


class CompanyTable(JoblessTable):
    SCHEMA = CompanySchema
    BORDER_TITLE = "companies"
    COLUMNS = [
        "id",
        "name",
        "url",
        "industry",
        "applications",
        "contacts",
    ]

    def item_to_row(self, item: CompanySchema) -> tuple:
        return (
            str(item.id),
            item.name,
            item.url if item.url else "N/A",
            item.industry if item.industry else "N/A",
            str(len(item.applications)),
            str(len(item.contacts)),
        )


class ApplicationTable(JoblessTable):
    SCHEMA = ApplicationSchema
    BORDER_TITLE = "applications"
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

    def item_to_row(self, item: ApplicationSchema) -> tuple:
        return (
            str(item.id),
            item.title,
            item.company.label,
            item.status,
            str(item.priority),
            str(len(item.contacts)),
            ", ".join(skill.label for skill in item.skills),
            self.format_date(item.date_applied),
            self.format_date(item.follow_up_date),
        )


class ContactTable(JoblessTable):
    SCHEMA = ContactSchema
    BORDER_TITLE = "contacts"
    COLUMNS = [
        "id",
        "name",
        "email",
        "phone",
        "url",
        "companies",
        "applications",
    ]

    def item_to_row(self, item: ContactSchema) -> tuple:
        return (
            str(item.id),
            item.name,
            item.email if item.email else "N/A",
            item.phone if item.phone else "N/A",
            item.url if item.url else "N/A",
            str(len(item.companies)),
            str(len(item.applications)),
        )
