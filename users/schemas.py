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

# class Settings(BaseModel):
#     authjwt_secret_key: str = "f9a66e677041e94b29df770d56979cf3178504f792c15a5da9511a4ea9064fa8"