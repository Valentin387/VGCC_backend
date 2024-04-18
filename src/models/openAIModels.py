from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EventCreateInput(BaseModel):
    summary: str
    location: Optional[str] = None
    description: Optional[str] = None
    start: str  # RFC3339 datetime
    end: str    # RFC3339 datetime
    attendees: Optional[List[EmailStr]] = []
    reminders: Optional[List[dict]] = []

class InputText(BaseModel):
    input_text: str
