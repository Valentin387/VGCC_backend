from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EventCreateInput(BaseModel):
    summary: str
    location: Optional[str] = None
    description: Optional[str] = None
    start: str  # Start time in RFC3339 text format, e.g., "2020-06-01T10:00:00-07:00"
    end: str    # End time in RFC3339 text format
    attendees: Optional[List[EmailStr]] = []
    reminders: Optional[List[dict]] = []
    
class InputText(BaseModel):
    input_text: str

class InputBoolean(BaseModel):
    input_boolean: bool




