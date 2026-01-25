from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationInfo,
    field_validator,
)

from jobless.models import Location, Status


class SkillSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1)

    applications: list[ApplicationSchema] = []


class ContactSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr | None = None
    phone: str | None = None
    url: str | None = None
    notes: str | None = None

    companies: list[CompanySchema] = []
    applications: list[ApplicationSchema] = []


class CompanySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    website: str | None = None
    industry: str | None = None
    notes: str | None = None

    applications: list[ApplicationSchema] = []
    contacts: list[ContactSchema] = []


class ApplicationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str | None = None
    salary_range: str | None = None
    platform: str | None = None
    url: str | None = None
    address: str | None = None
    location_type: Location | None = None
    status: Status = Status.SAVED
    priority: int = Field(default=0, ge=0, le=4)
    date_applied: date | None = None
    follow_up_date: date | None = None
    notes: str | None = None

    company: CompanySchema | None = None
    skills: list[SkillSchema] = []
    contacts: list[ContactSchema] = []

    @field_validator("follow_up_date")
    @classmethod
    def validate_correct_follow_up(cls, v: date, info: ValidationInfo):
        if v and info.data.get("date_applied") and v < info.data["date_applied"]:
            raise ValueError("Follow up date cannot be before application date.")

        return v
