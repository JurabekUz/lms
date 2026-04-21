from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

class SchoolBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)

class SchoolCreateRequest(SchoolBase):
    pass

class SchoolResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class SchoolListResponse(BaseModel):
    items: list[SchoolResponse]
    total: int
    limit: int
    offset: int

