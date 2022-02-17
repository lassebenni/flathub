from time import sleep
from dataclasses import dataclass
from datetime import datetime

from gcalendar.gcalendar import Calendar


@dataclass
class EarningsEvent:
    start_date: str
    name: str
    short_float: str
    description: str = ""
    summary: str = ""
    location: str = ""

    def __post_init__(self):
        self.summary = f"{self.name} ({self.short_float}%)"
        self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()


class EarningsCalendar:
    def __init__(self, calendar: Calendar):
        self.calendar = calendar
        self.service = calendar.calendar.service

    def list_earnings_events(self):
        return self.calendar.list_events(query="", time_min=datetime.now())

    def select_earnings_calendar(self):
        calendars = self.calendar.list_secondary_calendars()
        finance_cal = [x for x in calendars if "Yahoo" in x["summary"]][0]
        self.calendar.switch_calendar(finance_cal["id"])

    def create_earnings_calendar(self):
        calendar_body = {
            "description": "Calendar for Earnings Announcements for shorted stocks",
            "summary": "Yahoo Finance Earnings Calendar",
            "timeZone": "Europe/Amsterdam",
        }
        earnings_calendar = (
            self.service.calendars().insert(body=calendar_body).execute()
        )

        self.calendar.switch_calendar(earnings_calendar["id"])

    def add_earnings_event(self, event: EarningsEvent):
        return self.calendar.add_event(
            summary=event.summary, location=event.location, start_date=event.start_date,
        )

    def delete_earnings_events(self):
        earnings_events = self.list_earnings_events()

        for event in earnings_events:
            self.calendar.delete_event(event)
            sleep(5)