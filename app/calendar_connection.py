from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

# OAuth 2.0 setup


def event_exists(service, start_time, summary, calendar_id='primary'):
    # Format the time range for querying (using 1-minute buffer for precision)
    min_time = datetime.datetime.fromisoformat(start_time).isoformat() + 'Z'
    max_time = (datetime.datetime.fromisoformat(start_time) + datetime.timedelta(minutes=1)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=min_time,
        timeMax=max_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    for event in events:
        if event['summary'] == summary:
            return True
    return False

def create_events_from_list(service, events_list, calendar_id='primary'):
    for start_time, summary in events_list:
        if not event_exists(service, start_time, summary, calendar_id):
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',  # Replace 'UTC' with your preferred time zone if needed
                },
                'end': {
                    'dateTime': (datetime.datetime.fromisoformat(start_time) + datetime.timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                },
            }
            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Event created: {created_event.get('htmlLink')}")
        else:
            print(f"Event '{summary}' at {start_time} already exists.")

def init_get_calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('/auth/cred.json', SCOPES)
    creds = flow.run_local_server(port=8080)

    # Build the Calendar API service
    service = build('calendar', 'v3', credentials=creds)
    return service

if __name__ == "__main__":
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('../auth/cred.json', SCOPES)
    creds = flow.run_local_server(port=8080)

    # Build the Calendar API service
    service = build('calendar', 'v3', credentials=creds)
    events_list = [
        ("2024-11-15T14:00:00", "Meeting with team")
        # Add more events as needed
    ]
    create_events_from_list(service, events_list)