from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette import status
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt, JWTError
from datetime import datetime, timedelta

from database import get_db
from users.models import User, TokenBlacklist
from users.schemas import (
    SignUpSchema, LoginSchema,
    ProfileUpdateSchema, PasswordUpdateSchema,
    RefreshTokenSchema
)

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()

SECRET_KEY = "f9a66e677041e94b29df770d56979cf3178504f792c15a5da9511a4ea9064fa8"
ALGORITHM = "HS256"


def create_token(username: str, token_type: str) -> str:
    expire = datetime.utcnow() + (
        timedelta(minutes=30) if token_type == "access" else timedelta(days=7)
    )
    data = {"sub": username, "type": token_type, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz yoki muddati tugagan"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials

    if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token blacklistga tushgan. Qayta login qiling."
        )

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token talab qilinadi"
        )

    user = db.query(User).filter(User.username == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Hisob faol emas")

    return user


@router.post('/sign-up', status_code=status.HTTP_201_CREATED)
def sign_up(user: SignUpSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Bu username band")

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Bu email band")

    new_user = User(
        username=user.username,
        first_name=user.first_name,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return JSONResponse(status_code=201, content={
        "status": 201,
        "message": "User yaratildi",
        "data": {
            "username": new_user.username,
            "first_name": new_user.first_name,
            "email": new_user.email
        }
    })


@router.post('/login')
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="Bu username topilmadi")

    if not check_password_hash(user.password, data.password):
        raise HTTPException(status_code=400, detail="Parol xato")

    return JSONResponse(content={
        "status": 200,
        "message": "Muvaffaqiyatli login",
        "access_token": create_token(data.username, "access"),
        "refresh_token": create_token(data.username, "refresh")
    })


@router.post('/refresh')
def refresh_token(data: RefreshTokenSchema, db: Session = Depends(get_db)):
    if db.query(TokenBlacklist).filter(TokenBlacklist.token == data.refresh_token).first():
        raise HTTPException(status_code=401, detail="Refresh token yaroqsiz")

    payload = decode_token(data.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token talab qilinadi")

    return JSONResponse(content={
        "status": 200,
        "message": "Token yangilandi",
        "access_token": create_token(payload.get("sub"), "access"),
        "refresh_token": create_token(payload.get("sub"), "refresh")
    })


@router.get('/profile')
def get_profile(current_user: User = Depends(get_current_user)):
    return JSONResponse(content={
        "status": 200,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "first_name": current_user.first_name,
            "email": current_user.email,
            "is_staff": current_user.is_staff,
            "is_active": current_user.is_active,
            "created_at": str(current_user.created_at),
            "updated_at": str(current_user.updated_at),
        }
    })


@router.patch('/profile/update')
def update_profile(
    data: ProfileUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.email and data.email != current_user.email:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Bu email allaqachon ishlatilmoqda")
        current_user.email = data.email

    if data.first_name is not None:
        current_user.first_name = data.first_name

    current_user.updated_at = datetime.now()
    db.commit()
    db.refresh(current_user)

    return JSONResponse(content={
        "status": 200,
        "message": "Profil yangilandi",
        "data": {
            "username": current_user.username,
            "first_name": current_user.first_name,
            "email": current_user.email,
            "updated_at": str(current_user.updated_at),
        }
    })


@router.patch('/password/update')
def update_password(
    data: PasswordUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_password_hash(current_user.password, data.old_password):
        raise HTTPException(status_code=400, detail="Eski parol noto'g'ri")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Yangi parollar mos kelmadi")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgidan iborat bo'lishi kerak")

    current_user.password = generate_password_hash(data.new_password)
    current_user.updated_at = datetime.now()
    db.commit()

    return JSONResponse(content={"status": 200, "message": "Parol muvaffaqiyatli yangilandi"})


@router.post('/logout')
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
        raise HTTPException(status_code=400, detail="Token allaqachon yaroqsiz")

    db.add(TokenBlacklist(token=token))
    db.commit()

    return JSONResponse(content={"status": 200, "message": "Muvaffaqiyatli chiqildi"})


@router.delete('/account/deactivate')
def deactivate_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    current_user.is_active = False
    current_user.updated_at = datetime.now()
    db.add(TokenBlacklist(token=token))
    db.commit()

    return JSONResponse(content={"status": 200, "message": "Hisob deaktivatsiya qilindi"})