from fastapi import APIRouter
from models.calendarModels import InputBoolean
from services.calendar_service import (
    get_credentials_info, authorize_accounts, get_calendar_events, delete_tokens
)

calendar_router = APIRouter()

@router.get("/credentials-info", response_model=list, tags=["Calendar"])
async def credentials_info_endpoint():
    """
    Endpoint to get information about the stored credentials.
    """
    return await get_credentials_info()

@router.post("/authorize", tags=["Calendar"])
async def authorize(input_data: InputBoolean):
    """
    Endpoint to authorize Google Calendar accounts.
    """
    return await authorize_accounts(input_data)

@router.post("/event", response_model=dict, tags=["Calendar"])
async def create_event(event_data: EventCreateInput):
    """
    Endpoint to create a new calendar event.
    """
    return await create_calendar_event(event_data)

@router.post("/event", tags=["Calendar"])
async def create_event(event_data: EventCreateInput):
    return await create_calendar_event(event_data)

@router.delete("/delete-tokens", tags=["Calendar"])
async def tokens_delete():
    """
    Endpoint to delete stored credentials.
    """
    return await delete_tokens()
