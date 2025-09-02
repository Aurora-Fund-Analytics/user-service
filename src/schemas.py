from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str | None = None
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: str
    username: str
    full_name: Optional[str]
    join_date: datetime
    cash_balance: float
    holdings: Dict[str, int]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None