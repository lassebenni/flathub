import logging
import os
from typing import List

from gcalendar.gcalendar import Calendar
from nu_headlines.nu_calendar import NUHeadlinesCalendar
from nu_headlines.nu_headlines import Headline, NUHeadlines
from shortbet.shortbet_calendar import EarningsCalendar

from shortbet.shortbet_earnings import ShortbetEarnings

from gsheets.sheets import GoogleSheet

logger = logging.getLogger(__name__)


def main():
    sheet_credentials_path = os.getenv("GOOGLE_SHEET_CREDENTIALS_PATH")
    sheet = GoogleSheet(sheet_credentials_path)

    email = os.environ.get("CALENDAR_EMAIL")
    token_bucket = os.environ.get("TOKEN_BUCKET")
    calendar = Calendar(email, token_bucket)

    earnings_to_calendar(calendar, sheet)
    nu_headlines_to_calendar(calendar, sheet)


def earnings_to_calendar(calendar: Calendar, sheet: GoogleSheet):
    earnings = ShortbetEarnings()
    tickers = earnings.crawl()

    df = earnings.tickers_to_df(tickers)
    sheet.connect(sheet="shortbet", worksheet="shortbet")
    sheet.update_sheet(df)

    earnings_calendar = EarningsCalendar(calendar)
    earnings_calendar.select_earnings_calendar()
    earnings_calendar.delete_earnings_events()
    events = earnings_calendar.tickers_to_events(tickers)
    earnings_calendar.add_earnings_events(events)

    logger.info(f"Added {len(tickers)} earnings events")


def nu_headlines_to_calendar(calendar: Calendar, sheet: GoogleSheet):
    logger.info("Processing NU headlines")
    nu_hl = NUHeadlines()
    headlines: List[Headline] = nu_hl.crawl()
    df = nu_hl.headlines_to_df(headlines)
    sheet.connect(sheet="nu_headlines", worksheet="headlines")
    sheet.update_sheet(df)

    most_read_headline = [headline for headline in headlines if headline.rank == 1][0]
    calendar = NUHeadlinesCalendar(calendar)
    calendar.select_nu_calendar()
    calendar.delete_todays_headline()
    calendar.add_nu_headline_event(most_read_headline)

    logger.info(f"Added most recent NU.nl headline")


if __name__ == "__main__":
    main()
    logger.info("Done")
