from pydantic import BaseModel, EmailStr
from typing import Optional


class SignUpSchema(BaseModel):
    first_name: Optional[str] = None
    username: str
    email: EmailStr
    password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "first_name": "Nargiza",
                "username": "Nargiza10",
                "email": "omonboyeva00@gmail.com",
                "password": "password123"
            }
        }
    }


class LoginSchema(BaseModel):
    username: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "Nargiza10",
                "password": "password123"
            }
        }
    }


class ProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Nargiza",
                "email": "new_email@gmail.com"
            }
        }
    }


class PasswordUpdateSchema(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "password123",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456"
            }
        }
    }


class RefreshTokenSchema(BaseModel):
    refresh_token: str