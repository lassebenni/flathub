# Google-Calendar-Flathub

Repository to connect FlatHub (Github Action scrapers) repositories to Google Calendar.

Steps

1. Provision S3 Bucket.
2. Create Google Sheets Secret. Download as JSON. Store in S3 Bucket.
3. Repeat for Google Calendar Secret.
4. Create `.env` from `.env.example`. Fill in the path to the secrets.
5. Add `CALENDER_EMAIL` for google calendar access.
