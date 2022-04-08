from datetime import datetime as dt
import logging
from typing import Dict, List, Optional
import json
from dataclasses import dataclass, fields
import uuid

import requests  # type: ignore
import desert
import pandas as pd

COMMITS_URL = "https://api.github.com/repos/lassebenni/shortbet/commits?per_page=1"

SHORT_TRESHOLD = 15

logger = logging.getLogger(__name__)


@dataclass
class Ticker:
    datetime: str
    earnings_date: str
    name: str
    short_float: float
    symbol: str
    url: str
    ingestion_datetime: str = dt.now().isoformat()
    price: Optional[float] = None
    id: str = str(uuid.uuid4())


class ShortbetEarnings:
    def __init__(self):
        self.ticker_schema = desert.schema(Ticker)

    def crawl(self) -> List[Ticker]:
        tickers: List[Ticker] = []

        commit_sha = self._fetch_latest_commit_sha()
        url = f"https://raw.githubusercontent.com/lassebenni/shortbet/{commit_sha}/data/latest.json"

        logger.info(f"Fetching {url}")
        res = requests.get(url)
        if res and res.text:
            tickers_json = json.loads(res.text)
            for ticker_json in tickers_json:
                if (
                    not "earnings_date" in ticker_json
                    or not ticker_json["earnings_date"]
                ):
                    continue  # can't work with empty earnings date

                earnings_date = dt.strptime(ticker_json["earnings_date"], "%Y-%m-%d")
                if earnings_date < dt.now():
                    continue  # Only care about future earnings

                if (
                    "short_float" not in ticker_json
                    or ticker_json["short_float"] < SHORT_TRESHOLD
                ):
                    continue  # Need short float to be higher than threshold

                if "price" in ticker_json and ticker_json["price"] == "":
                    ticker_json["price"] = 0

                if "name" in ticker_json and not ticker_json["name"]:
                    ticker_json["name"] = ticker_json["symbol"]

                tickers.append(self.ticker_schema.load(ticker_json))

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

    def tickers_to_df(self, tickers: List[Ticker]) -> pd.DataFrame:
        ticker_dicts: List[Dict] = [
            desert.schema(Ticker).dump(ticker) for ticker in tickers
        ]
        df = pd.DataFrame.from_dict(ticker_dicts)
        # order columns since desert doesn't guarantee the ordering
        ordered_columns = [field.name for field in fields(Ticker)]
        df = df[ordered_columns]
        return df
