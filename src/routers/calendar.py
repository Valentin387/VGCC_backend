#Libraries
from fastapi import HTTPException, APIRouter
import os.path
import json
from fastapi.responses import JSONResponse
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request


# Initialize FastAPI router
calendar_router = APIRouter()

#set the scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Function to parse dates from ISO 8601 format
def parse_iso_date(date_str):
    return datetime.datetime.fromisoformat(date_str)

def get_credentials():
    """Retrieve stored credentials from tokens.json."""
    if os.path.exists("tokens.json"):
        with open("tokens.json", "r") as token_file:
            tokens = json.load(token_file)
            return [Credentials.from_authorized_user_info(json.loads(token), SCOPES) for token in tokens]
    return []

def save_credentials(creds):
    """Save credentials to tokens.json."""
    tokens = []
    if os.path.exists("tokens.json"):
        with open("tokens.json", "r") as token_file:
            tokens = json.load(token_file)
    tokens.append(creds.to_json())
    with open("tokens.json", "w") as token_file:
        json.dump(tokens, token_file)


@calendar_router.post("/authorize", tags=["calendar"])
async def authorize_accounts(addNewAccount: bool = False):
    """Shows basic usage of the Google Calendar API."""
    creds_list = get_credentials()
    if not creds_list:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        save_credentials(creds)
        creds_list = [creds]
    elif addNewAccount:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0, authorization_prompt_message="Select the account to use or add a new one: ")
        save_credentials(creds)
        creds_list.append(creds)


@calendar_router.get("/get-calendar-events", tags=["calendar"])
async def get_calendar_events(start: str, end: str):
    try:
        if not start or not end:
            raise HTTPException(status_code=422, detail="Missing start_date or end_date in request body")

        creds_list = get_credentials()
        if not creds_list:
            raise HTTPException(status_code=401, detail="No authorized accounts found. Please authorize an account first.")

        cont=1
        # Create a list to store events for all users
        all_events = {}
        for creds in creds_list:
            user_events = await fetch_user_events(creds, start, end, cont)
            all_events[f"User {cont}"] = user_events  # Add user_events with formatted key
            cont+=1
        return all_events
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")


async def fetch_user_events(creds, start: str, end: str, numuser: int):
    service = build("calendar", "v3", credentials=creds)
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No events found for user %d" %numuser)
    else:
        user_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            user_events.append({"start": start, "summary": event["summary"]})
        return user_events  # Add user_events with formatted key