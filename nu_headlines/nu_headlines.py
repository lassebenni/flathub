from datetime import datetime
from typing import Dict, List
import json
from dataclasses import dataclass, fields
import uuid

import requests  # type: ignore
import desert
import pandas as pd
from helpers.github import fetch_latest_commit_sha


COMMITS_URL = "https://api.github.com/repos/lassebenni/nu_nl_scraper/commits?per_page=1"

SHORT_TRESHOLD = 15


@dataclass
class Headline:
    date: str
    title: str
    url: str
    rank: int
    ingestion_datetime: str = datetime.now().isoformat()
    id: str = str(uuid.uuid4())


class NUHeadlines:
    def __init__(self):
        self.headline_schema = desert.schema(Headline)

    def crawl(self) -> List[Headline]:
        headlines: List[Headline] = []

        commit_sha = fetch_latest_commit_sha(COMMITS_URL)
        url = f"https://raw.githubusercontent.com/lassebenni/nu_nl_scraper/{commit_sha}/output/results.json"

        res = requests.get(url)
        if res and res.text:
            result_json = json.loads(res.text)
            today_str = datetime.today().strftime("%Y-%m-%d")

            for headline_json in result_json:
                date = headline_json["datetime"].split("T")[
                    0
                ]  # e.g. '2020-04-01T00:00:00'
                if date != today_str:
                    continue  # Only care about today's headline
                else:
                    headline_json["date"] = date

                headlines.append(
                    self.headline_schema.load(headline_json, unknown="exclude")
                )

        return headlines

    def headlines_to_df(self, headlines: list[Headline]) -> pd.DataFrame:
        headline_dicts: List[Dict] = [
            desert.schema(Headline).dump(headline) for headline in headlines
        ]
        df = pd.DataFrame.from_dict(headline_dicts)
        # order columns since desert doesn't guarantee the ordering
        ordered_columns = [field.name for field in fields(Headline)]
        df = df[ordered_columns]
        return df
