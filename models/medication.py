from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

DoseUnit = Literal["mg", "mcg", "g", "mL", "units", "puffs", "drops"]
Frequency = Literal["once_daily", "twice_daily", "three_times_daily", "as_needed", "other"]


class MedicationBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Medication ID.",
        json_schema_extra={"example": "22222222-3333-4444-9999-aaaaaaaaaaaa"},
    )
    person_id: UUID = Field(
        ...,
        description="FK to Person.id.",
        json_schema_extra={"example": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"},
    )
    name: str = Field(
        ...,
        description="Medication name.",
        json_schema_extra={"example": "Amoxicillin"},
    )
    dose: Optional[float] = Field(
        None, description="Dose amount (numeric).", json_schema_extra={"example": 500}
    )
    dose_unit: Optional[DoseUnit] = Field(
        None, description="Dose unit.", json_schema_extra={"example": "mg"}
    )
    frequency: Frequency = Field(
        "as_needed",
        description="Simple frequency label.",
        json_schema_extra={"example": "twice_daily"},
    )
    instructions: Optional[str] = Field(
        None,
        description="Free-text instructions.",
        json_schema_extra={"example": "Take with food."},
    )
    start_date: Optional[date] = Field(
        None, description="Start date.", json_schema_extra={"example": "2025-02-01"}
    )
    end_date: Optional[date] = Field(
        None, description="End/stop date.", json_schema_extra={"example": "2025-02-10"}
    )
    is_current: bool = Field(
        False,
        description="True if currently taking.",
        json_schema_extra={"example": True},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "22222222-3333-4444-9999-aaaaaaaaaaaa",
                    "person_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
                    "name": "Loratadine",
                    "dose": 10,
                    "dose_unit": "mg",
                    "frequency": "once_daily",
                    "instructions": "Take in the morning.",
                    "start_date": "2025-03-01",
                    "end_date": None,
                    "is_current": True,
                }
            ]
        }
    }


class MedicationCreate(MedicationBase):
    """Creation payload for a medication."""
    pass


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dose: Optional[float] = None
    dose_unit: Optional[DoseUnit] = None
    frequency: Optional[Frequency] = None
    instructions: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"dose": 5, "dose_unit": "mL"},
                {"is_current": False, "end_date": "2025-02-10"},
            ]
        }
    }


class MedicationRead(MedicationBase):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "22222222-3333-4444-9999-aaaaaaaaaaaa",
                    "person_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
                    "name": "Loratadine",
                    "dose": 10,
                    "dose_unit": "mg",
                    "frequency": "once_daily",
                    "instructions": "Take in the morning.",
                    "start_date": "2025-03-01",
                    "end_date": None,
                    "is_current": True,
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
