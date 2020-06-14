from datetime import datetime, timedelta
from environs import Env
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.context import CryptContext
from src.models.user.user import User, Token, TokenData
from uuid import uuid4 as uuid
import jwt


# Router for the API
ROUTER = APIRouter()

# Enviroment reader
env = Env()
env.read_env()

SECRET_KEY = env.str("SECRET_KEY")
ALGORITHM = env.str("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = env.int(
    "ACCESS_TOKEN_EXPIRE_MINUTES", default=30
)

fake_users_db = {
    "johndoe": {
        "id": "f8707ff9-b1ef-4293-b6a9-556fc7d00000",
        "username": "johndoe",
        "name": "John Doe",
        "password": "$2b$12$IQ4abOA7/ePXBlXZn4yDlOf9GsAy7sACWodKqer61svPZIf2hTy.2",
        "nickname": "johnny",
        "email": "john@email.com",
        "created_at": "2020-05-11 19:34:37.482168",
        "updated_at": "2020-05-11 19:34:37.482168"
    },
    "alice": {
        "id": "7be514e6-63eb-4ebb-9e23-f4aa47e426bc",
        "username": "alice",
        "name": "Alice Wonderson",
        "password": "$2b$12$IQ4abOA7/ePXBlXZn4yDlOf9GsAy7sACWodKqer61svPZIf2hTy.2",
        "nickname": "wonderalice",
        "email": "alice@email.com",
        "created_at": "2020-05-11 19:34:37.482168",
        "updated_at": "2020-05-11 19:34:37.482168"
    },
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)


def authenticate_user(database, username: str, password: str):
    user = get_user(database, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
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
    # TODO: Update Current Active User Logic
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Routes
@ROUTER.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(
        fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@ROUTER.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@ROUTER.get("/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
