import json
import logging
import s3fs

from gspread_pandas import Spread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

logger = logging.getLogger(__name__)


class GoogleSheet:
    def __init__(self, credentials_path: str):
        self.credentials = self._get_credentials(credentials_path)

    def _get_credentials(self, path: str):
        with s3fs.S3FileSystem().open(path, "rb") as f:
            token = f.read()

            return ServiceAccountCredentials.from_json_keyfile_dict(
                json.loads(token), scope
            )

    def connect(self, sheet: str, worksheet: str = None):
        self.spread = Spread(
            spread=sheet,
            sheet=worksheet,
            create_spread=True,
            create_sheet=True,
            creds=self.credentials,
        )

    def update_sheet(self, df, worksheet_name=None, replace_sheet: bool = False):
        if not self.spread:
            logger.error("Not connected to spreadsheet.")
            return

        self.spread.df_to_sheet(
            df,
            index=False,
            sheet=worksheet_name,
            start="A1",
            replace=replace_sheet,
            freeze_headers=True,
        )

    # if this is the first time the sheet is being used, you have to run this after creation
    def share_sheet(self, email: str):
        for sheet in self.spread.sheets:
            sheet.spreadsheet.share(email, "user", "writer")
