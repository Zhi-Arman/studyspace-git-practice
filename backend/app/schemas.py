"""Bounded write payloads. Extra properties cannot grant privileges."""

import re
from datetime import date
from typing import Annotated, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

Password = Annotated[str, StringConstraints(strip_whitespace=False)]


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Register(Payload):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_]+$")
    display_name: str = Field(min_length=1, max_length=60)
    password: Password = Field(min_length=10, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        value = value.lower()
        if value.startswith("deleted_"):
            raise ValueError("Reserved username")
        return value


class Login(Payload):
    username: str = Field(min_length=1, max_length=32)
    password: Password = Field(min_length=1, max_length=128)


class CreateBooking(Payload):
    seat_id: int = Field(gt=0)
    starts_at: AwareDatetime
    ends_at: AwareDatetime


class CancelBooking(Payload):
    reason: str | None = Field(default=None, max_length=240)


def clock_minutes(value: str, *, end: bool = False) -> int:
    if end and value == "24:00":
        return 1440
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):(?:00|30)", value):
        raise ValueError("Use a half-hour boundary, for example 08:00.")
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


class RoomInput(Payload):
    name: str = Field(min_length=1, max_length=80)
    campus: str = Field(min_length=1, max_length=60)
    building: str = Field(min_length=1, max_length=60)
    floor: int = Field(ge=-5, le=100)
    kind: Literal["CLASSROOM", "STUDY_ROOM"]
    description: str = Field(default="", max_length=240)
    enabled: bool = True
    opens_at: str = "08:00"
    closes_at: str = "22:00"
    reason: str = Field(default="", max_length=240)

    @model_validator(mode="after")
    def check_hours(self):
        if clock_minutes(self.opens_at) >= clock_minutes(self.closes_at, end=True):
            raise ValueError("Opening must precede closing.")
        return self


class SeatInput(Payload):
    room_id: int = Field(gt=0)
    code: str = Field(min_length=1, max_length=24)
    enabled: bool = True
    reason: str = Field(default="", max_length=240)


class ExceptionInput(Payload):
    room_id: int = Field(gt=0)
    day: date
    closed: bool = False
    opens_at: str = "08:00"
    closes_at: str = "22:00"
    reason: str = Field(min_length=1, max_length=240)

    @model_validator(mode="after")
    def check_hours(self):
        if clock_minutes(self.opens_at) >= clock_minutes(self.closes_at, end=True):
            raise ValueError("Opening must precede closing.")
        return self


class UserUpdate(Payload):
    enabled: bool
    role: Literal["STUDENT", "ADMIN"]
    reason: str = Field(min_length=1, max_length=240)


class PolicyUpdate(Payload):
    advance_days: int = Field(ge=1, le=7)
    reason: str = Field(min_length=1, max_length=240)
