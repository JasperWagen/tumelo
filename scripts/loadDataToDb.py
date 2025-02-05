import os

import pandas as pd

from src.orm.orm import GeneralMeeting, Organisation, Proposal


def importCsvToDb(csv_path: str):
    testing = os.environ.get("TESTING") == "True"
    data = pd.read_csv(csv_path)

    data["Meeting Date"] = data["Meeting Date"].apply(lambda x: pd.to_datetime(x, format="%d/%m/%Y"))

    badRecommendationDf = data[~data["Recommendation"].isin(["For", "Against", "Abstain"])]
    data = data[data["Recommendation"].isin(["For", "Against", "Abstain"])]

    if not badRecommendationDf.empty:
        if testing is True:
            raise ValueError

        print("Found incorrect recommendations, removing from import and saving to disk")
        badRecommendationDf.to_csv("badRecommendations.csv")

    orgSeqGroups = (
        data.groupby(["Organisation Name", "Sequence Identifier", "Meeting Date"])
        .size()
        .reset_index()
        .rename(columns={0: "count"})
    )
    duplicatedOrgSeq = orgSeqGroups[orgSeqGroups["count"] > 1]

    if not duplicatedOrgSeq.empty:
        if testing is True:
            raise ValueError

        print("Found duplicated rows, saving to disk and removing from import")
        duplicatedOrgSeq.to_csv("duplicatedRows.csv")

    data = data[
        ~data.set_index(["Organisation Name", "Meeting Date", "Sequence Identifier"]).index.isin(
            duplicatedOrgSeq.set_index(["Organisation Name", "Meeting Date", "Sequence Identifier"]).index
        )
    ]

    for _, row in data.iterrows():
        org, _ = Organisation.get_or_create(name=row["Organisation Name"])
        meeting, _ = GeneralMeeting.get_or_create(organisation_id=org, date=row["Meeting Date"])
        Proposal.create(
            general_meeting_id=meeting,
            identifier=row["Sequence Identifier"],
            text=row["Proposal Text"],
            recommendation=row["Recommendation"],
        )


if __name__ == "__main__":
    importCsvToDb("testData/Example Recommendations[67].csv")
