from enum import StrEnum


class Status(StrEnum):
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"
    CLOSED = "Closed"
    WITHDRAWN = "Withdrawn"


class Location(StrEnum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"
