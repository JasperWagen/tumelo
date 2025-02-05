import os
import uuid

from peewee import SQL, CharField, Check, DateField, ForeignKeyField, Model, SqliteDatabase, UUIDField

testing = os.environ.get("TESTING") == "True"

if testing is True:
    db_path = "file:cachedb?mode=memory&cache=shared"
else:
    db_path = "recommendations.db"

db = SqliteDatabase(db_path)


class OrmBaseModel(Model):
    class Meta:
        database = db


class Organisation(OrmBaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(unique=True)

    class Meta:
        table_name = "organisation"


class GeneralMeeting(OrmBaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    organisation_id = ForeignKeyField(Organisation, backref="meetings", on_delete="CASCADE")
    date = DateField()

    class Meta:
        table_name = "general_meeting"


class Proposal(OrmBaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    general_meeting_id = ForeignKeyField(GeneralMeeting, backref="proposals", on_delete="CASCADE")
    identifier = CharField()
    text = CharField()
    recommendation = CharField(constraints=[Check("recommendation IN ('For', 'Against', 'Abstain')")])

    class Meta:
        table_name = "proposal"
        constraints = [SQL("UNIQUE (general_meeting_id, identifier)")]
