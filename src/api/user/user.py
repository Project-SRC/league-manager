from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.utils.utils import get_object_by_id
from jwt import PyJWTError
from passlib.context import CryptContext
from src.db.db import run
from src.models.user.user import User, Token, TokenData
from src.service.service import get_variable
import jwt
import ujson as json


# Router for the API
ROUTER = APIRouter()

# Enviroment reader
SECRET_KEY = get_variable("SECRET_KEY")
ALGORITHM = get_variable("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = get_variable("ACCESS_TOKEN_EXPIRE_MINUTES", int) or 30
DATABASE = get_variable("RDB_DB", str) or "LEAGUE"

# Global variables
TABLE = "user"
NOW = str(datetime.now())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str):
    operation = "filter"
    data = {"username": username, "deleted_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return User.parse_obj(database_obj.get("response_message")[0])
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def create_user(user: dict):
    operation = "insert"
    data = json.loads(User.parse_obj({**user}).json())
    data.pop("id")
    payload = {"database": DATABASE, "table": TABLE, "data": data}
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    else:
        data.update(
            {"id": database_obj.get("response_message").get("generated_keys")[0]}
        )
        return User.parse_obj(data)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
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
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Deleted User")
    return current_user


# Routes
@ROUTER.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
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
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}


@ROUTER.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@ROUTER.post("/register")
async def register_user(form_data: dict):
    user = await create_user(form_data)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}


@ROUTER.delete("/close/{identifier}")
async def close_account(identifier: str):
    # Soft remove (no data is deleted)
    exists = await get_object_by_id(identifier, DATABASE, TABLE, User)
    if exists:
        operation = "update"
        data = {"updated_at": NOW, "deleted_at": NOW}
        payload = {
            "database": DATABASE,
            "table": TABLE,
            "identifier": identifier,
            "data": data,
        }
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Database couldn't delete the object. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            return {"detail": f"{identifier} deleted"}
    else:
        raise HTTPException(
            status_code=403, detail=f"Driver with ID {identifier} doesn't exist."
        )
