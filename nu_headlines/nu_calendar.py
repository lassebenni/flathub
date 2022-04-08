from datetime import datetime

from gcalendar.gcalendar import Calendar
from nu_headlines.nu_headlines import Headline

CALENDAR_NAME = "NU.nl"


class NUHeadlinesCalendar(Calendar):
    def __init__(self, calendar: Calendar):
        self.calendar = calendar

    def select_nu_calendar(self):
        calendars = self.calendar.list_secondary_calendars()
        nu_calendar = [x for x in calendars if CALENDAR_NAME in x["summary"]][0]
        self.calendar.switch_calendar(nu_calendar["id"])

    def create_nu_calendar(self):
        calendar_body = {
            "description": "Calendar for NU.nl headlines",
            "summary": "NU.nl Most Popular Headlines",
            "timeZone": "Europe/Amsterdam",
        }
        nu_calendar = (
            self.calendar.service.calendars().insert(body=calendar_body).execute()
        )

        self.calendar.switch_calendar(nu_calendar["id"])

    def add_nu_headline_event(self, headline: Headline):
        return self.calendar.add_event(
            summary=headline.title,
            location=headline.url,
            start_date=headline.date,
        )

    def delete_todays_headline(self):
        events = self.calendar.list_events(query="", time_min=datetime.today())

        for event in events:
            self.calendar.delete_event(event)
