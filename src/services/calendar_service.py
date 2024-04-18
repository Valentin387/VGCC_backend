import os
import json
from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models.calendarModels import InputBoolean, EventCreateInput

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKENS_FILE = 'tokens.json'
CLIENT_SECRETS_FILE = 'credentials.json'

async def get_credentials_info():
    """
    Retrieve stored credentials from tokens.json.
    """
    if not os.path.exists(TOKENS_FILE):
        return []
    with open(TOKENS_FILE, 'r') as token_file:
        tokens = json.load(token_file)
        credentials_info = [
            {"name": f"User {idx + 1}", "expiry": token['expiry']} for idx, token in enumerate(tokens)
        ]
    return credentials_info

async def authorize_accounts(input_data: InputBoolean):
    """
    Authorize or reauthorize Google Calendar accounts.
    """
    add_new_account = input_data.input_boolean
    if not os.path.exists(TOKENS_FILE) or add_new_account:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        save_credentials(creds)
        return {"message": "Authorization successful"}
    else:
        return {"message": "Authorization is already set"}

def save_credentials(creds):
    """
    Save credentials to tokens.json.
    """
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as token_file:
            tokens = json.load(token_file)
    else:
        tokens = []
    tokens.append(json.loads(creds.to_json()))
    with open(TOKENS_FILE, 'w') as token_file:
        json.dump(tokens, token_file)

async def get_calendar_events(start: str, end: str):
    """
    Fetch calendar events for authorized accounts within a specified time range.
    """
    if not start or not end:
        raise HTTPException(status_code=400, detail="Start or end date parameter is missing")
    creds_list = get_credentials()
    if not creds_list:
        raise HTTPException(status_code=401, detail="No authorized accounts found")
    
    events_list = []
    for creds in creds_list:
        service = build('calendar', 'v3', credentials=creds)
        events_result = service.events().list(
            calendarId='primary', timeMin=start, timeMax=end,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        events_list.extend(events)

    return events_list

async def create_calendar_event(event_data: EventCreateInput):
    creds_list = get_credentials()
    if not creds_list:
        raise HTTPException(status_code=401, detail="No authorized accounts found")
    
    event_body = {
        'summary': event_data.summary,
        'location': event_data.location,
        'description': event_data.description,
        'start': {
            'dateTime': event_data.start,
            'timeZone': event_data.time_zone,
        },
        'end': {
            'dateTime': event_data.end,
            'timeZone': event_data.time_zone,
        },
        'attendees': [{'email': attendee} for attendee in event_data.attendees],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    for creds in creds_list:
        service = build('calendar', 'v3', credentials=creds)
        try:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
            return {"message": "Event created", "event_id": event['id']}
        except HttpError as error:
            raise HTTPException(status_code=500, detail=str(error))

async def delete_tokens():
    """
    Delete tokens.json file which stores credentials.
    """
    if not os.path.exists(TOKENS_FILE):
        raise HTTPException(status_code=404, detail="Credentials file not found")
    os.remove(TOKENS_FILE)
    return {"message": "Stored tokens deleted successfully"}

def get_credentials():
    """
    Helper function to load credentials from tokens.json.
    """
    if not os.path.exists(TOKENS_FILE):
        return []
    with open(TOKENS_FILE, 'r') as token_file:
        tokens = json.load(token_file)
    return [Credentials(token) for token in tokens]
