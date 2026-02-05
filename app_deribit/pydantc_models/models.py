"""
This module contains Pydantic models (schemas) for the Deribit project.

These models are used for:
1. Creating records: Sending new price data to the database.
2. Selecting records: Reading data from the database for the FastAPI.
"""


from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, AfterValidator, AwareDatetime, ConfigDict, field_validator, computed_field

from app_deribit.core.config_env_variable import local_zone


def timestamp_validator(value: int) -> int:
    """
    Changes the time format from microseconds to seconds.

    Args:
        value: The time value from Deribit (in microseconds).
    Returns:
        The time value in seconds (standard Unix timestamp).
    """
    return value // 1000000


class DeribitIndex(BaseModel):
    """
    Base model for Deribit index price data.

    This class validates data from the Deribit API and prepares it
    to be saved in the database. It stores the price with high precision
    and converts the timestamp to seconds.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    ticker: str
    price: Annotated[
        Decimal,
        Field(max_digits=16, decimal_places=8)
    ]
    timestamp: Annotated[int, AfterValidator(timestamp_validator)]



class DeribitTimeZone(DeribitIndex):
    created_at: AwareDatetime | None = None
    """
    Model for displaying data with local time.

    It inherits all fields from DeribitIndex but changes the
    'created_at' time zone. It automatically converts UTC time
    from the database into Moscow time (Europe/Moscow).
    """

    @field_validator('created_at', mode='after')
    @classmethod
    def time_zone_validator(cls, value: datetime) -> datetime:
        """
        Converts UTC datetime to Moscow time zone.
        Args:
            value: The datetime object in UTC.
        Returns:
            The datetime object in Moscow time (UTC+3).
        """
        return value.astimezone(tz = local_zone)


class DateFilterStart(BaseModel):
    """
    Class to collect date parts from the user.
    """
    start_year: Annotated[int, Field(ge=2016, le=2031, description="Year")] = 2016
    start_month: Annotated[int, Field(ge=1, le=12, description="Month")] = 1
    start_day: Annotated[int, Field(ge=1, le=31, description="Day")] = 1
    start_hour: Annotated[int, Field(ge=0, le=23, description="Hour")] = 0
    start_minute: Annotated[int, Field(ge=0, le=59, description="Minute")] = 0

    model_config = ConfigDict(from_attributes=True)





    @computed_field
    @property
    def dt_object(self) -> datetime:
        """
        Creates a datetime object from separate fields. This uses for select with between.
        """

        try:
            actual_time = datetime(
                self.start_year,
                self.start_month,
                self.start_day,
                self.start_hour,
                self.start_minute,
                tzinfo=local_zone,
            )
            print("Дата корректна!")
            return actual_time.astimezone(timezone.utc)
        except ValueError as e:
            print("Ошибка: такой даты не существует")
            raise ValueError(f"Invalid calendar date: {e}")

class DateFilterEnd(BaseModel):
    """
    Class to collect date parts from the user . This uses for select with between.
    """
    end_year: Annotated[int, Field(ge=2016, le=2031, description="Year")] = 2031
    end_month: Annotated[int, Field(ge=1, le=12, description="Month")] = 1
    end_day: Annotated[int, Field(ge=1, le=31, description="Day")] = 1
    end_hour: Annotated[int, Field(ge=0, le=23, description="Hour")] = 0
    end_minute: Annotated[int, Field(ge=0, le=59, description="Minute")] = 0

    model_config = ConfigDict(from_attributes=True)


    @computed_field
    @property
    def dt_end_object(self) -> datetime:
        """
        Creates a datetime object from separate fields.
        """

        try:
            actual_time = datetime(
                self.end_year,
                self.end_month,
                self.end_day,
                self.end_hour,
                self.end_minute,
                tzinfo=local_zone,
            )
            print("Дата корректна!")
            return actual_time.astimezone(timezone.utc)
        except ValueError as e:
            print("Ошибка: такой даты не существует")
            raise ValueError(f"Invalid calendar date: {e}")



class DeribitListResponse(BaseModel):
    """
    Model to show a list of prices with extra information.
    """
    ticker: str
    count: int
    data: list[DeribitTimeZone]
