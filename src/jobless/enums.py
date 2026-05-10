from enum import StrEnum


class Status(StrEnum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    GHOSTED = "ghosted"
    CLOSED = "closed"
    WITHDRAWN = "withdrawn"


class Location(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on-site"


class OutputFormat(StrEnum):
    TABLE = "table"
    LIST = "list"
    JSON = "json"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ApplicationSortField(StrEnum):
    TITLE = "title"
    COMPANY = "company"
    STATUS = "status"
    DATE_APPLIED = "date"
    FOLLOW_UP_DATE = "follow_up"
    CREATED = "created"
    UPDATED = "updated"


class CompanySortField(StrEnum):
    NAME = "name"
    NUMBER_APPLICATIONS = "number_applications"
    CREATED = "created"
    UPDATED = "updated"


class ContactSortField(StrEnum):
    NAME = "name"
    EMAIL = "email"
    NUMBER_APPLICATIONS = "number_applications"
    CREATED = "created"
    UPDATED = "updated"
