from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ReleveRequest(BaseModel):
    filename: str
    content: str

class Entity(BaseModel):
    text: str
    label: str

class ReleveResponse(BaseModel):
    id: str
    filename: str
    content: str
    extracted_entities: List[Entity]

class ReleveListItem(BaseModel):
    id: str
    filename: str
    created_at: str