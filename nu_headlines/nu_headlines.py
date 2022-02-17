from datetime import datetime
from typing import List, Optional
import requests
import json
from dataclasses import dataclass

from helpers.github import fetch_latest_commit_sha


COMMITS_URL = "https://api.github.com/repos/lassebenni/nu_nl_scraper/commits?per_page=1"

SHORT_TRESHOLD = 15


@dataclass
class NUHeadline:
    date: str
    title: str
    url: float
    rank: int

    def __post_init__(self):
        self.date = datetime.strptime(self.date, "%Y-%m-%d").date()


def crawl() -> List[NUHeadline]:
    headlines: List[NUHeadline] = []

    commit_sha = fetch_latest_commit_sha(COMMITS_URL)
    url = f"https://raw.githubusercontent.com/lassebenni/nu_nl_scraper/{commit_sha}/output/results.json"

    res = requests.get(url)
    if res and res.text:
        result_json = json.loads(res.text)
        today_str = datetime.today().strftime("%Y-%m-%d")

        for headline_json in result_json:
            date = headline_json["datetime"].split("T")[0]  # e.g. '2020-04-01T00:00:00'
            if date != today_str:
                continue  # Only care about today's headline

            headlines.append(
                NUHeadline(
                    date=date,
                    rank=headline_json["rank"],
                    title=headline_json["title"],
                    url=headline_json["url"],
                )
            )

    return headlines
