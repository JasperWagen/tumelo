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
    assert len(orgs) == 20

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


def testBadRecommendations(createDbTables):
    with pytest.raises(ValueError):
        importCsvToDb("testData/badRecommendations.csv")


def testDuplicatedRows(createDbTables):
    with pytest.raises(ValueError):
        importCsvToDb("testData/duplicatedRows.csv")
