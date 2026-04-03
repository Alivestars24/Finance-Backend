from pydantic import BaseModel, Field
from datetime import date

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(pattern="^(viewer|analyst|admin)$")


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str


class RecordCreate(BaseModel):
    amount: float
    type: str = Field(pattern="^(income|expense)$")
    category: str
    date: date
    notes: str | None = None
    owner_id: int | None = None


class RecordOut(RecordCreate):
    id: int

    class Config:
        from_attributes = True