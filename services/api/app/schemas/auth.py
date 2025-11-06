"""Authentication schemas."""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    tenant_id: int
    role: str


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    tenant_name: str


class RegisterResponse(BaseModel):
    """Registration response schema."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    tenant_id: int
