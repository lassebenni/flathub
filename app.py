import os
from time import sleep
from typing import List

from gcalendar.gcalendar import Calendar
from nu_headlines.nu_calendar import NUHeadlinesCalendar

from shortbet.shortbet_calendar import EarningsCalendar, EarningsEvent
from shortbet.shortbet_earnings import ShortbetEarnings
import nu_headlines.nu_headlines as nu


def main():
    email = os.environ.get("CALENDAR_EMAIL")
    token_bucket = os.environ.get("TOKEN_BUCKET")
    calendar = Calendar(email, token_bucket)

    earnings_to_calendar(calendar)
    nu_headlines_to_calendar(calendar)


def earnings_to_calendar(calendar: Calendar):
    earnings_calendar = EarningsCalendar(calendar)
    earnings_calendar.select_earnings_calendar()
    earnings_calendar.delete_earnings_events()
    earnings = ShortbetEarnings()
    tickers = earnings.crawl()
    for ticker in tickers:
        event = EarningsEvent(
            location=ticker.url,
            name=ticker.name,
            short_float=ticker.short_float,
            start_date=ticker.earnings_date,
        )
        earnings_calendar.add_earnings_event(event)
        sleep(5)

    print(f"Added {len(tickers)} earnings events")


def nu_headlines_to_calendar(calendar: Calendar):
    nu_headlines: List[nu.NUHeadline] = nu.crawl()
    if nu_headlines:
        most_read_headline = [
            headline for headline in nu_headlines if headline.rank == 1
        ][0]

        nu_calendar = NUHeadlinesCalendar(calendar)
        nu_calendar.select_nu_calendar()
        nu_calendar.delete_todays_headline()
        nu_calendar.add_nu_headline_event(most_read_headline)

    print(f"Added most recent NU.nl headline")


if __name__ == "__main__":
    main()
    print("Done")
