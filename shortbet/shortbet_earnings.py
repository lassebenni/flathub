from datetime import datetime
from typing import List, Optional
import requests
import json
from dataclasses import dataclass

import desert

COMMITS_URL = "https://api.github.com/repos/lassebenni/shortbet/commits?per_page=1"

SHORT_TRESHOLD = 15


@dataclass
class Shortbet:
    datetime: str
    earnings_date: str
    name: str
    short_float: float
    symbol: str
    url: str
    price: Optional[float] = None


class ShortbetEarnings:
    def __init__(self):
        self.ticker_schema = desert.schema(Shortbet)

    def crawl(self) -> List[Shortbet]:
        tickers: List[Shortbet] = []

        commit_sha = self._fetch_latest_commit_sha()
        url = f"https://raw.githubusercontent.com/lassebenni/shortbet/{commit_sha}/data/latest.json"

        res = requests.get(url)
        if res and res.text:
            tickers_json = json.loads(res.text)
            for ticker in tickers_json:
                if not "earnings_date" in ticker or not ticker["earnings_date"]:
                    continue  # can't work with empty earnings date

                earnings_date = datetime.strptime(ticker["earnings_date"], "%Y-%m-%d")
                if earnings_date < datetime.now():
                    continue  # Only care about future earnings

                if (
                    "short_float" not in ticker
                    or ticker["short_float"] < SHORT_TRESHOLD
                ):
                    continue  # Need short float to be higher than threshold

                if "price" in ticker and ticker["price"] == "":
                    ticker["price"] = 0

                if "name" in ticker and not ticker["name"]:
                    ticker["name"] = ticker["symbol"]

                tickers.append(self.ticker_schema.load(ticker))

        return tickers

    def _fetch_latest_commit_sha(self) -> str:
        commit_sha = None

        response = requests.get(COMMITS_URL)
        if response and response.text:
            commit = json.loads(response.text)[0]
            if commit:
                commit_sha = commit["sha"]

        if commit_sha:
            return commit_sha
        else:
            raise Exception("Could not fetch latest commit sha")
