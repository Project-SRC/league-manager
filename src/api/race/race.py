from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import CreateRace, RaceResponse, UpdateRace

ROUTER = APIRouter()

TABLE = "race"
TRACK_TABLE = "track"


@ROUTER.get("/{identifier}", response_model=RaceResponse)
async def get_race(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()
    result = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Traceback: {result.error}",
        )
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Race with ID {identifier} not found")

    return RaceResponse.model_validate(result.data[0])


@ROUTER.post("/", response_model=RaceResponse)
async def create_race(race: CreateRace, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()

    if race.track_id:
        track_result = await connector.execute(
            "select", {"table": TRACK_TABLE, "filters": {"id": str(race.track_id)}}
        )
        if track_result.error or not track_result.data:
            raise HTTPException(status_code=404, detail="Track not found")

    race_dict = race.model_dump()
    if race_dict.get("id") is None:
        race_dict.pop("id", None)

    insert_result = await connector.execute("insert", {"table": TABLE, "data": race_dict})
    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_race = insert_result.data[0]
    return RaceResponse.model_validate(created_race)


@ROUTER.patch("/{identifier}", response_model=RaceResponse)
async def update_race(
    body: UpdateRace, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=403, detail="Object not found on database.")

    update_data = {k: v for k, v in body.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(UTC)

    result = await connector.execute(
        "update", {"table": TABLE, "data": update_data, "filters": {"id": identifier}}
    )
    if result.error:
        raise HTTPException(
            status_code=409,
            detail=f"Database couldn't update the object with the ID {identifier}. Traceback: {result.error}",
        )

    updated = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if not updated.data:
        raise HTTPException(status_code=404, detail="Race not found after update")
    return RaceResponse.model_validate(updated.data[0])


@ROUTER.delete("/{identifier}")
async def remove_race(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Race with ID {identifier} not found")

    update_data = {
        "updated_at": datetime.now(UTC),
        "deleted_at": datetime.now(UTC),
    }
    result = await connector.execute(
        "update", {"table": TABLE, "data": update_data, "filters": {"id": identifier}}
    )
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't delete the object with the ID {identifier}. Traceback: {result.error}",
        )
    return {"detail": f"{identifier} deleted"}


@ROUTER.options("/")
async def describe_route():
    return {
        "GET": "/v1/race/{identifier}",
        "DELETE": "/v1/race/{identifier}",
        "PATCH": "/v1/race/{identifier}",
        "POST": "/v1/race/",
    }
