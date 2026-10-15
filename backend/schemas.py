from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str


class ResendOTP(BaseModel):
    email: EmailStr


class JobCreate(BaseModel):
    title: str
    company: str
    description: str


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    description: str

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: int
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True