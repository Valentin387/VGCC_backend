from typing import List
from pydantic import BaseModel


class InputText(BaseModel):
    input_text: str

class InputBoolean(BaseModel):
    input_boolean: bool




