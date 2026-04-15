from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette import status
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta

from database import engine
from users.models import User
from users.schemas import SignUpSchema, LoginSchema

router = APIRouter(prefix='/auth', tags=['auth'])
session = Session(bind=engine)

SECRET_KEY = "f9a66e677041e94b29df770d56979cf3178504f792c15a5da9511a4ea9064fa8"
ALGORITHM = "HS256"


def create_token(username: str, token_type: str) -> str:
    expire = datetime.utcnow() + (
        timedelta(minutes=30) if token_type == "access" else timedelta(days=7)
    )
    data = {"sub": username, "type": token_type, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@router.post('/sign-up', status_code=status.HTTP_201_CREATED)
def sign_up(user: SignUpSchema):
    if session.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu username band"
        )

    if session.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email band"
        )

    new_user = User(
        username=user.username,
        first_name=user.first_name,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return JSONResponse(
        content={
            "status": 201,
            "message": "User yaratildi",
            "data": {
                "username": new_user.username,
                "first_name": new_user.first_name,
                "email": new_user.email
            }
        },
        status_code=status.HTTP_201_CREATED
    )


@router.post('/login', status_code=status.HTTP_200_OK)
def login(data: LoginSchema):
    db_user = session.query(User).filter(User.username == data.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu username topilmadi"
        )

    if not check_password_hash(db_user.password, data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parol xato"
        )

    return JSONResponse(content={
        "status": 200,
        "message": "Muvaffaqiyatli login",
        "access_token": create_token(data.username, "access"),
        "refresh_token": create_token(data.username, "refresh")
    })