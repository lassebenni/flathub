import json
import s3fs

from gspread_pandas import Spread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheet:
    def __init__(self, sheet_name, credentials_path: str):
        credentials = self._get_credentials(credentials_path)
        self.spread = Spread(sheet_name, creds=credentials)

    def _get_credentials(self, path: str):
        with s3fs.S3FileSystem().open(path, "rb") as f:
            token = f.read()

            return ServiceAccountCredentials.from_json_keyfile_dict(
                json.loads(token), scope
            )

    def update_sheet(self, df, worksheet_name, replace_sheet: bool = False):
        self.spread.df_to_sheet(
            df, index=False, sheet=worksheet_name, start="A1", replace=replace_sheet
        )
