from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import CreateTrack, TrackResponse, UpdateTrack

ROUTER = APIRouter()

TABLE = "track"
COUNTRY_TABLE = "country"


@ROUTER.get("/{identifier}", response_model=TrackResponse)
async def get_track(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()
    result = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Traceback: {result.error}",
        )
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Track with ID {identifier} not found")

    track_data = result.data[0]
    if track_data.get("deleted_at"):
        raise HTTPException(status_code=409, detail=f"Object with ID {identifier} is deleted.")

    return TrackResponse.model_validate(track_data)


@ROUTER.post("/", response_model=TrackResponse)
async def create_track(track: CreateTrack, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()

    if track.country_id:
        country_result = await connector.execute(
            "select", {"table": COUNTRY_TABLE, "filters": {"id": str(track.country_id)}}
        )
        if country_result.error or not country_result.data:
            raise HTTPException(status_code=404, detail="Country not found")

    track_dict = track.model_dump()
    if track_dict.get("id") is None:
        track_dict.pop("id", None)

    insert_result = await connector.execute("insert", {"table": TABLE, "data": track_dict})
    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_track = insert_result.data[0]
    return TrackResponse.model_validate(created_track)


@ROUTER.patch("/{identifier}", response_model=TrackResponse)
async def update_track(
    body: UpdateTrack, identifier: str, current_user: User = Depends(get_current_active_user)
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
        raise HTTPException(status_code=404, detail="Track not found after update")
    return TrackResponse.model_validate(updated.data[0])


@ROUTER.delete("/{identifier}")
async def remove_track(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Track with ID {identifier} not found")

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
        "GET": "/v1/track/{identifier}",
        "DELETE": "/v1/track/{identifier}",
        "PATCH": "/v1/track/{identifier}",
        "POST": "/v1/track/",
    }
