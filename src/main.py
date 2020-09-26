from fastapi import FastAPI
from api.team.contract import ROUTER as CONTRACT
from api.country.country import ROUTER as COUNTRY
from api.user.driver import ROUTER as DRIVER
from api.league.league import ROUTER as LEAGUE
from api.user.manager import ROUTER as MANAGER
from api.race.participation import ROUTER as PARTICIPATION
from api.race.race import ROUTER as RACE
from api.user.steward import ROUTER as STEWARD
from api.team.team import ROUTER as TEAM
from api.track.track import ROUTER as TRACK
from api.user.user import ROUTER as USER
from service.service import get_variable
import uvicorn

MOCK = get_variable("MOCK", bool) or False
TEST = get_variable("TEST", bool) or False
VERSION = get_variable("VERSION", str) or "0.0.1"

league = FastAPI(
    title="League API 🏎🏆🏁", description="Project SRC - API", version=VERSION
)

# Add Custom Models and Routes
league.include_router(COUNTRY, prefix="/v1/country", tags=["Country"])
league.include_router(LEAGUE, prefix="/v1/league", tags=["League"])
league.include_router(PARTICIPATION, prefix="/v1/race", tags=["Race"])
league.include_router(RACE, prefix="/v1/race", tags=["Race"])
league.include_router(TEAM, prefix="/v1/team", tags=["Team"])
league.include_router(CONTRACT, prefix="/v1/team", tags=["Team"])
league.include_router(TRACK, prefix="/v1/track", tags=["Track"])
league.include_router(USER, prefix="/v1/user", tags=["User"])
league.include_router(DRIVER, prefix="/v1/user", tags=["User"])
league.include_router(MANAGER, prefix="/v1/user", tags=["User"])
league.include_router(STEWARD, prefix="/v1/user", tags=["User"])


@league.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("main:league", host="127.0.0.1", port=8000, reload=True)
