import s3fs
from gcsa.google_calendar import GoogleCalendar


class CalendarAuth:
    def __init__(self, token_bucket: str, token_path: str = "token.pickle"):
        # mount S3 bucket as filesystem
        self.fs = s3fs.S3FileSystem()
        self.bucket = token_bucket
        self.token_path = token_path

    def authenticate(self, email: str) -> GoogleCalendar:
        self._read_token()
        # creating the calendar also updates the token
        calendar = GoogleCalendar(email, token_path=self.token_path)
        self._overwrite_token()
        return calendar

    def _read_token(self):
        token = self._read_token_from_s3()
        self._write_token(token)

    def _read_token_from_s3(self):
        token_path = f"{self.bucket}/{self.token_path}"

        with self.fs.open(token_path, "rb") as f:
            return f.read()

    def _write_token(self, token: bytes):
        with open(self.token_path, "wb") as token_file:
            token_file.write(token)

    def _overwrite_token(self):
        with open(self.token_path, "rb") as local_token:
            token = local_token.read()
            # overwrite token in Bucket
            with self.fs.open(f"{self.bucket}/{self.token_path}", "wb") as bucket_token:
                bucket_token.write(token)
