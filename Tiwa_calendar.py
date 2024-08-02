import datetime
import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class Tiwa_GoogleCalendarAPI:
    def __init__(self, token_file="token.json", credentials_file="credentials.json"):
        self.token_file = token_file
        self.credentials_file = credentials_file
        self.calendar_id = "ab002238bd56e5fc0252b50fc274ea35d8cb230e5eb7abfdc4da4a5372446ed7@group.calendar.google.com"
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Handles authentication and token management."""
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as token:
                token.write(self.creds.to_json())

        self.service = build("calendar", "v3", credentials=self.creds)

    def list_events(self, max_results=10, timezone="Asia/Bangkok"):
        """Lists the upcoming events on the user's calendar."""
        now = datetime.datetime.now().isoformat() + "Z"
        print("Getting the upcoming events")
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                    timeZone=timezone,
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                print("No upcoming events found!")
                return "No upcoming events found!"

            events_list = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                event_details = f"Event ID: {event['id']}, Start: {start}, Summary: {event['summary']}"
                print(event_details)
                events_list.append(event_details)

            return "\n".join(events_list)

        except HttpError as error:
            error_message = f"An error occurred: {error}"
            print(error_message)
            return error_message

    def list_events_json(self, max_results=10, timezone="Asia/Bangkok"):
        """Lists the upcoming events on the user's calendar in JSON format."""
        now = datetime.datetime.now().isoformat() + "Z"
        print("Getting the upcoming 10 events in JSON format")
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                    timeZone=timezone,
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                print("No upcoming events found!")
                return json.dumps([])

            events_list = []
            for event in events:
                event_data = {
                    "id": event["id"],
                    "summary": event["summary"],
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                }
                events_list.append(event_data)

            return json.dumps(events_list, indent=2)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return json.dumps([])

    def create_event(self, summary, start_time, duration, timezone="Asia/Bangkok"):
        """Creates a new event in the user's calendar."""
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": (
                    datetime.datetime.fromisoformat(start_time)
                    + datetime.timedelta(minutes=duration)
                ).isoformat(),
                "timeZone": timezone,
            },
        }

        try:
            event_result = (
                self.service.events()
                .insert(calendarId=self.calendar_id, body=event)
                .execute()
            )
            event_details = f"Event created: {event_result['id']}, Start: {event_result['start']['dateTime']}, Summary: {event_result['summary']}"
            print(event_details)
            return event_details
        except HttpError as error:
            error_message = f"An error occurred: {error}"
            print(error_message)
            return error_message

    def delete_event(self, event_id):
        """Deletes an event from the user's calendar if it exists."""
        try:
            event = (
                self.service.events()
                .get(calendarId=self.calendar_id, eventId=event_id)
                .execute()
            )
            event_details = f"Event to be deleted: {event['id']}, Start: {event['start'].get('dateTime', event['start'].get('date'))}, Summary: {event['summary']}"

            try:
                self.service.events().delete(
                    calendarId=self.calendar_id, eventId=event_id
                ).execute()
                delete_message = f"Event deleted: {event_details}"
                print(delete_message)
                return delete_message
            except HttpError as error:
                error_message = f"An error occurred while deleting the event: {error}"
                print(error_message)
                return error_message
        except HttpError as error:
            if error.resp.status == 404:
                not_found_message = f"Event with ID {event_id} does not exist."
                print(not_found_message)
                return not_found_message
            else:
                error_message = f"An error occurred while checking the event: {error}"
                print(error_message)
                return error_message


if __name__ == "__main__":
    google_calendar = Tiwa_GoogleCalendarAPI()
    google_calendar.list_events()

    # # Example usage of creating an event:
    # event_name = "Meeting with Team"
    # start_time = "2024-07-27T15:00:00"  # ISO 8601 format: YYYY-MM-DDTHH:MM:SS
    # duration = 60  # duration in minutes
    # google_calendar.create_event(event_name, start_time, duration)

    # Example usage of deleting an event (replace 'event_id_here' with a valid event ID obtained from list_events output):
    # event_id = (
    #     "g807oudsgnp5av2rb4hdaafcfo"  # Replace with the actual event ID to delete
    # )
    # google_calendar.delete_event(event_id)

    # Example usage of listing events in JSON format:
    # events_json = google_calendar.list_events_json()
    # print(events_json)
