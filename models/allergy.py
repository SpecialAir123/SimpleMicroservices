from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

AllergySeverity = Literal["mild", "moderate", "severe"]
AllergyType = Literal["drug", "food", "environment", "other"]


class AllergyBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Allergy ID.",
        json_schema_extra={"example": "11111111-2222-4333-8444-555555555555"},
    )
    person_id: UUID = Field(
        ...,
        description="FK to Person.id.",
        json_schema_extra={"example": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"},
    )
    allergen: str = Field(
        ...,
        description="Allergen name.",
        json_schema_extra={"example": "Peanuts"},
    )
    allergy_type: AllergyType = Field(
        "food",
        description="Type/category of allergy.",
        json_schema_extra={"example": "food"},
    )
    reaction: Optional[str] = Field(
        None,
        description="Typical reaction (free text).",
        json_schema_extra={"example": "Hives, swelling"},
    )
    severity: AllergySeverity = Field(
        "moderate",
        description="Clinical severity (coarse).",
        json_schema_extra={"example": "severe"},
    )
    noted_date: Optional[date] = Field(
        None,
        description="Date allergy first documented.",
        json_schema_extra={"example": "2023-05-20"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "11111111-2222-4333-8444-555555555555",
                    "person_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
                    "allergen": "Peanuts",
                    "allergy_type": "food",
                    "reaction": "Hives, swelling",
                    "severity": "severe",
                    "noted_date": "2023-05-20",
                }
            ]
        }
    }


class AllergyCreate(AllergyBase):
    """Creation payload for an allergy."""
    pass


class AllergyUpdate(BaseModel):
    allergen: Optional[str] = None
    allergy_type: Optional[AllergyType] = None
    reaction: Optional[str] = None
    severity: Optional[AllergySeverity] = None
    noted_date: Optional[date] = None

    model_config = {
        "json_schema_extra": {"examples": [{"severity": "mild"}, {"reaction": "Rash"}]}
    }


class AllergyRead(AllergyBase):
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
                    "id": "11111111-2222-4333-8444-555555555555",
                    "person_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
                    "allergen": "Peanuts",
                    "allergy_type": "food",
                    "reaction": "Hives, swelling",
                    "severity": "severe",
                    "noted_date": "2023-05-20",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
