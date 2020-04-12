from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.user.user import User, UserInDB, Token, TokenData
from src.user.user import (
    authenticate_user,
    create_access_token,
    get_user,
    fake_decode_token,
    get_current_user,
    get_current_active_user,
)
from src.user.user import fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
import ujson as json

league = FastAPI(
  title="League API 🏎🏆🏁",
  description="This is a very fancy project, with auto docs for the API and everything",
  version="0.0.1",
  redoc_url=None,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@league.get("/")
async def read_root():
    return {"Hello": "World"}


@league.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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


@league.get("/items/{item_id}")
async def read_item(item_id: int, query: str = None):
    return {"item_id": item_id, "query": query}


@league.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@league.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@league.get("/docs")
async def get_documentation(current_user: User = Depends(get_current_active_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


if __name__ == "__main__":
    uvicorn.run("src.main:league", host="127.0.0.1", port=8000, reload=True)
