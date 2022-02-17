import base64
from datetime import date, datetime
from typing import List

from gcsa.google_calendar import Event
from gcalendar.authentication import CalendarAuth

COLOR_ID_BLUE = "1"

IGNORED_CALENDARS = [
    "Feestdagen in Nederland",
    "Verjaardagen",
]


class Calendar:
    def __init__(self, email: str, token_bucket: str):
        self.auth = CalendarAuth(token_bucket)
        self.calendar = self.auth.authenticate(email)
        self.calendar_id = email
        self.service = self.calendar.service

    def __iter__(self):
        return iter(self.list_events())

    def list_events(self, query: str, time_min: datetime) -> List[Event]:
        return self.calendar.get_events(query=query, time_min=time_min)

    def add_event(
        self,
        summary: str,
        location: str,
        start_date: date,
        color_id: str = COLOR_ID_BLUE,
    ):
        return self.calendar.add_event(
            Event(
                summary=summary,
                location=location,
                start=start_date,
                end=None,
                color=color_id,
            )
        )

    def update_event(self, event: Event):
        print("update event")
        pass

    def delete_event(self, event: Event):
        return self.calendar.delete_event(event)

    def list_secondary_calendars(self) -> list:
        calendar_list = self.calendar.service.calendarList().list().execute()
        calendars = [
            calendar
            for calendar in calendar_list["items"]
            if calendar["summary"] not in IGNORED_CALENDARS
        ]
        return calendars

    def create_secondary_calendar(
        self,
        description: str,
        location: str,
        summary: str,
        timezone: str = "Europe/Amsterdam",
    ):
        calendar_body = {
            "description": description,
            "location": location,
            "summary": summary,
            "timeZone": timezone,
        }

        return self.calendar.service.calendars().insert(body=calendar_body).execute()

    def switch_calendar(self, email: str):
        self.calendar = self.auth.authenticate(email)
        self.calendar_id = email

    def get_calendar_link(self, calendar_id: str):
        calendarId_bytes = calendar_id.encode("utf-8")
        cid_base64 = base64.b64encode(calendarId_bytes)
        cid = cid_base64.decode().rstrip("=")

        return f"https://calendar.google.com/calendar/u/0?cid={cid}"

    def set_public_access(self):
        rule = {
            "scope": {
                "type": "default",
            },
            "role": "reader",
        }

        return (
            self.calendar.service.acl()
            .insert(calendarId=self.calendar_id, body=rule)
            .execute()
        )

    def delete_events(self, time_min: datetime):
        events = self.list_events(query="", time_min=time_min)

        for event in events:
            self.calendar.delete_event(event)
