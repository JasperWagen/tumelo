import pytest

from src.orm.orm import GeneralMeeting, Organisation, Proposal, db


@pytest.fixture
def createDbTables():
    db.connect()
    db.create_tables([Organisation, GeneralMeeting, Proposal])
    yield

    db.drop_tables([Organisation, GeneralMeeting, Proposal])
    db.close()


@pytest.fixture
def testAuthHeader():
    return {"api-key": "hello"}
