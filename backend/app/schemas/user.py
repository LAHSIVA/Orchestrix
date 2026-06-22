from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr

from app.models.enums import UserRole
from app.models.enums import UserStatus


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }