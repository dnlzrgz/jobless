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


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


# --- Company ---
class CompanyBase(BaseSchema):
    name: str = Field(..., min_length=1)
    website: str | None = None
    industry: str | None = None
    notes: str | None = None

    # application_ids: list[int] = []
    contact_ids: list[int] = []


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    name: str | None = Field(None, min_length=1)


# --- Contacts ---
class ContactBase(BaseSchema):
    name: str = Field(..., min_length=1)
    email: EmailStr | None = None
    phone: str | None = None
    url: str | None = None
    notes: str | None = None

    application_ids: list[int] = []
    company_ids: list[int] = []


class ContactCreate(ContactBase):
    # TODO: check that email and phone are unique
    pass


class ContactUpdate(ContactBase):
    name: str | None = Field(None, min_length=1)


# --- Skills ---
class SkillBase(BaseSchema):
    name: str = Field(..., min_length=1)
    application_ids: list[int] = []


class SkillCreate(SkillBase):
    pass


class SkillUpdate(SkillBase):
    pass


# --- Applications ---
class ApplicationBase(BaseSchema):
    title: str = Field(..., min_length=1)
    description: str | None = None
    company_id: int
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

    skill_names: list[str] = []
    contact_ids: list[int] = []

    @field_validator("follow_up_date")
    @classmethod
    def validate_correct_follow_up(cls, v: date, info: ValidationInfo):
        if v and info.data.get("date_applied") and v < info.data["date_applied"]:
            raise ValueError("follow up date cannot be before application date.")

        return v


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(ApplicationBase):
    title: str | None = Field(None, min_length=1)
    priority: int | None = Field(None, ge=0, le=4)
