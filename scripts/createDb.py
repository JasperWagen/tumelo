import os

from src.orm.orm import GeneralMeeting, Organisation, Proposal, db, db_path


def createDb():
    if os.path.exists(db_path):
        os.remove(db_path)

    db.connect()
    db.create_tables([Organisation, GeneralMeeting, Proposal])


if __name__ == "__main__":
    createDb()
