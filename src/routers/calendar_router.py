from fastapi import APIRouter
from ..services.calendar_service import get_credentials_info, authorize_accounts, get_calendar_events, delete_tokens

router = APIRouter()

@router.get("/credentials-info")
async def credentials_info_endpoint():
    return await get_credentials_info()

@router.post("/authorize")
async def authorize(input_data: InputBoolean):
    return await authorize_accounts(input_data)

@router.get("/events")
async def calendar_events(start: str, end: str):
    return await get_calendar_events(start, end)

@router.delete("/delete-tokens")
async def tokens_delete():
    return await delete_tokens()
