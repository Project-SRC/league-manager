from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from environs import Env
from src.api.user.user import ROUTER as USER
import uvicorn
import ujson as json

env = Env()
env.read_env()

MOCK = env.bool("MOCK", default=False)
TEST = env.bool("TEST", default=False)
VERSION = env.str("VERSION")

league = FastAPI(
    title="League API 🏎🏆🏁",
    description="Project SRC - API",
    version=VERSION
)

# Add Custom Models and Routes
league.include_router(USER, prefix="/user", tags=["User"])


@league.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("src.main:league", host="127.0.0.1", port=8000, reload=True)
