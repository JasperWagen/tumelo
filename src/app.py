from typing import Optional
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException

from src.models.proposals import GeneralMeeting, Organisation, Proposal
from src.orm import orm

app = FastAPI(
    title="Tumelo",
    version="0.0.1",
)


def check_api_key(api_key: str = Header(...)):
    if api_key != "hello":
        raise HTTPException(status_code=401, detail="incorrect API key")
    return api_key


@app.get("/organisations")
def list_organisations(api_key: str = Depends(check_api_key)) -> list[Organisation]:
    ormOrganisations = orm.Organisation.select().execute()
    return [Organisation.model_validate(org.__dict__["__data__"]) for org in ormOrganisations]


@app.get("/generalmeetings")
def list_general_meetings(
    organisation_id: Optional[UUID] = None, api_key: str = Depends(check_api_key)
) -> list[GeneralMeeting]:
    if organisation_id is None:
        return []

    ormGeneralMeetings = (
        orm.GeneralMeeting.select().where(orm.GeneralMeeting.organisation_id == organisation_id).execute()
    )
    return [GeneralMeeting.model_validate(meeting.__dict__["__data__"]) for meeting in ormGeneralMeetings]


@app.get("/proposals")
def list_proposals(general_meeting_id: Optional[UUID] = None, api_key: str = Depends(check_api_key)) -> list[Proposal]:
    if general_meeting_id is None:
        return []

    ormProposals = orm.Proposal.select().where(orm.Proposal.general_meeting_id == general_meeting_id).execute()
    return [Proposal.model_validate(meeting.__dict__["__data__"]) for meeting in ormProposals]
