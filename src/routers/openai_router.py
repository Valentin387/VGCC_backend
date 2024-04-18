from fastapi import APIRouter
from models.openAIModels import InputText, EventCreateInput
from services.openai_service import (get_llm_response, handle_text_deletion, handle_text_creation,
                                     handle_text_append, interpret_and_schedule_event)

router = APIRouter()

@router.post("/response/")
async def llm_response(input_text_data: InputText):
    return await get_llm_response(input_text_data)

@router.delete("/delete-text/")
async def delete_text():
    return await handle_text_deletion()

@router.post("/create-text/")
async def create_text():
    return await handle_text_creation()

@router.post("/append-text/")
async def append_text(input_data: InputText):
    return await handle_text_append(input_data)

@router.post("/schedule-event/")
async def schedule_event(input_text_data: InputText):
    """
    Endpoint to schedule a new event based on natural language input.
    """
    return await interpret_and_schedule_event(input_text_data)
