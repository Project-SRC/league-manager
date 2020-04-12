from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4 as uuid
from uuid import UUID
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

SECRET_KEY = "29da5bb8099920c0c62cb99eb48de9e2bd2ecc80af6aa1307ecd59c7490a4d6387987421de0e348e5479a65bcc7443a66a8fb2917d059d4fe030718549f19b26"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "id": "f8707ff9-b1ef-4293-b6a9-556fc7d00000",
        "username": "johndoe",
        "name": "John Doe",
        "password": "$2b$12$LSpjdEdGDXvWikH6huFgM.p1x5WMuSVZ8Qrw1d.Bdfa4l5pnMYL3G",
        "disabled": False,
    },
    "alice": {
        "id": "7be514e6-63eb-4ebb-9e23-f4aa47e426bc",
        "username": "alice",
        "name": "Alice Wonderson",
        "password": "$2b$12$K.N/n5EGPR01TvkfCpLQX.XG/1LBLARJqFG3133dTq73YcLp5Gf56",
        "disabled": True,
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    id: UUID
    username: str
    name: str
    disabled: Optional[bool] = None


class UserInDB(User):
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
