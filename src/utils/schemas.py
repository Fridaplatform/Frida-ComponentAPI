from typing import Optional
from pydantic import BaseModel

class ComponentRequest(BaseModel):
    prompt: str
    replaces: Optional[str] = ""