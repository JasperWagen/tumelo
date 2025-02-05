import pandas as pd
import pytest
from fastapi.testclient import TestClient

from scripts.loadDataToDb import importCsvToDb
from src.app import app

client = TestClient(app)


def testE2eSuccess(createDbTables, testAuthHeader):
    importCsvToDb("testData/cleanedRecommendations.csv")

    # Get Orgs
    orgResponse = client.get("/organisations", headers=testAuthHeader)
    assert orgResponse.status_code == 200

    orgs = orgResponse.json()
    assert len(orgs) == 33

    blinkOrgs = [org for org in orgs if org["name"] == "Blink Charging Co"]
    assert len(blinkOrgs) == 1

    blinkOrgId = blinkOrgs[0]["id"]

    # Get general meetings
    generalMeetingResponse = client.get(
        "/generalmeetings", headers=testAuthHeader, params={"organisation_id": blinkOrgId}
    )
    assert generalMeetingResponse.status_code == 200

    generalMeetings = generalMeetingResponse.json()
    assert len(generalMeetings) == 1

    generalMeetingId = generalMeetings[0]["id"]

    # Get proposals
    proposalsResponse = client.get(
        "/proposals", headers=testAuthHeader, params={"general_meeting_id": generalMeetingId}
    )
    assert proposalsResponse.status_code == 200

    proposals = proposalsResponse.json()
    assert len(proposals) == 9

    proposal3s = [proposal for proposal in proposals if proposal["identifier"] == "3"]
    assert len(proposal3s) == 1

    proposal3 = proposal3s[0]
    assert proposal3["recommendation"] == "For"


def testE2eRecreateCSV(createDbTables, testAuthHeader):
    importCsvToDb("testData/cleanedRecommendations.csv")

    orgResponse = client.get("/organisations", headers=testAuthHeader)
    assert orgResponse.status_code == 200

    orgs = orgResponse.json()

    for org in orgs:
        gmResponse = client.get("/generalmeetings", headers=testAuthHeader, params={"organisation_id": org["id"]})

        gms = gmResponse.json()
        for gm in gms:
            proposalsResponse = client.get(
                "/proposals", headers=testAuthHeader, params={"general_meeting_id": gm["id"]}
            )

            gm["proposals"] = proposalsResponse.json()

        org["meetings"] = gms

    apiDf = pd.json_normalize(
        orgs,
        ["meetings", "proposals"],
        record_prefix="proposal_",
        meta=["id", "name", ["meetings", "date"]],
        meta_prefix="organisation_",
    )

    apiDf.drop(columns=["proposal_id", "proposal_general_meeting_id", "organisation_id"], inplace=True)

    apiDf.rename(
        columns={
            "organisation_name": "Organisation Name",
            "proposal_text": "Proposal Text",
            "proposal_identifier": "Sequence Identifier",
            "proposal_recommendation": "Recommendation",
            "organisation_meetings.date": "Meeting Date",
        },
        inplace=True,
    )
    apiDf["Meeting Date"] = apiDf["Meeting Date"].apply(lambda x: pd.Timestamp(x).strftime("%d/%m/%Y"))
    apiDf = apiDf.sort_values(
        by=["Organisation Name", "Meeting Date", "Sequence Identifier"], ascending=[True, True, True]
    ).reset_index(drop=True)

    originalDf = pd.read_csv("testData/cleanedRecommendations.csv")
    originalDf = originalDf.sort_values(
        by=["Organisation Name", "Meeting Date", "Sequence Identifier"], ascending=[True, True, True]
    ).reset_index(drop=True)

    new_column_order = ["Meeting Date", "Organisation Name", "Sequence Identifier", "Proposal Text", "Recommendation"]

    apiDf = apiDf[new_column_order]
    originalDf = originalDf[new_column_order]

    assert apiDf.equals(originalDf)


def testBadRecommendations(createDbTables):
    with pytest.raises(ValueError):
        importCsvToDb("testData/badRecommendations.csv")


def testDuplicatedRows(createDbTables):
    with pytest.raises(ValueError):
        importCsvToDb("testData/duplicatedRows.csv")
