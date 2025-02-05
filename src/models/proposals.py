from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Organisation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class GeneralMeeting(BaseModel):
    id: UUID
    organisation_id: UUID
    date: date


class Proposal(BaseModel):
    id: UUID
    general_meeting_id: UUID
    text: str
    identifier: str
    recommendation: str
