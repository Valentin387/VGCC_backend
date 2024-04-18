from fastapi import APIRouter
from ..services.openai_service import get_llm_response, handle_text_deletion, handle_text_creation, handle_text_append

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
