from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
import ujson as json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError

from src.db.db import get_connector
from src.models.user.user import Token, TokenData, User
from src.schemas.pydantic import CreateUser
from src.security import verify_password
from src.service.service import get_variable

# Router for the API
ROUTER = APIRouter()

# Environment reader
SECRET_KEY = get_variable("SECRET_KEY")
ALGORITHM = get_variable("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = get_variable("ACCESS_TOKEN_EXPIRE_MINUTES", int) or 30
DATABASE = get_variable("RDB_DB", str) or "LEAGUE"

# Global variables
TABLE = "user"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


async def get_user(username: str):
    connector = get_connector()
    data: dict[str, Any] = {"username": username, "deleted_at": None}
    result = await connector.execute("select", {"table": TABLE, "filters": data})
    if result.error:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {result.error}",
        )
    if result.data and len(result.data) != 0:
        return User.model_validate(result.data[0])
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def create_user(user: dict[str, Any]):
    connector = get_connector()
    data = json.loads(User.model_validate({**user}).model_dump_json())
    data.pop("id")
    result = await connector.execute("insert", {"table": TABLE, "data": data})
    if result.error:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Check the database connection and parameters. Traceback: {result.error}",
        )
    elif result.data:
        data.update({"id": result.data[0].get("id")})
        return User.model_validate(data)
    else:
        raise HTTPException(
            status_code=500,
            detail="Database couldn't create the object. No data returned.",
        )


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(
    *, data: dict[str, Any], expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
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
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Deleted User")
    return current_user


# Routes
@ROUTER.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, UUID | str | None]:
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
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@ROUTER.post("/register")
async def register_user(form_data: CreateUser) -> dict[str, Any]:
    user = await create_user(form_data.model_dump())
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}


@ROUTER.delete("/close/{identifier}")
async def close_account(identifier: str):
    connector = get_connector()
    result = await connector.execute(
        "select", {"table": TABLE, "filters": {"id": identifier}}
    )
    if result.error:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {result.error}",
        )
    if not result.data:
        raise HTTPException(
            status_code=403, detail=f"User with ID {identifier} doesn't exist."
        )

    data = {
        "updated_at": datetime.now(UTC).isoformat(),
        "deleted_at": datetime.now(UTC).isoformat(),
    }
    result = await connector.execute(
        "update", {"table": TABLE, "data": data, "filters": {"id": identifier}}
    )
    if result.error:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't delete the object. Check the database connection and parameters. Traceback: {result.error}",
        )
    return {"detail": f"{identifier} deleted"}
