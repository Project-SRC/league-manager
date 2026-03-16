from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import CreateParticipation, ParticipationResponse, UpdateParticipation

ROUTER = APIRouter()

TABLE = "participation"
RACE_TABLE = "race"
DRIVER_TABLE = "driver"


@ROUTER.get("/{race}/participation/{identifier}", response_model=ParticipationResponse)
async def get_participation(
    race: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()
    result = await connector.execute(
        "select", {"table": TABLE, "filters": {"id": identifier, "race_id": race}}
    )
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Traceback: {result.error}",
        )
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Participation with ID {identifier} not found")

    return ParticipationResponse.model_validate(result.data[0])


@ROUTER.post("/{race}/participation", response_model=ParticipationResponse)
async def create_participation(
    participation: CreateParticipation,
    race: str,
    current_user: User = Depends(get_current_active_user),
):
    connector = get_connector()

    race_result = await connector.execute("select", {"table": RACE_TABLE, "filters": {"id": race}})
    if race_result.error or not race_result.data:
        raise HTTPException(status_code=404, detail=f"The Race with ID {race} doesn't exist")

    driver_result = await connector.execute(
        "select", {"table": DRIVER_TABLE, "filters": {"id": str(participation.driver_id)}}
    )
    if driver_result.error or not driver_result.data:
        raise HTTPException(
            status_code=404,
            detail=f"The Driver with ID {participation.driver_id} doesn't exist",
        )

    participation_dict = participation.model_dump()
    participation_dict["race_id"] = race
    if participation_dict.get("id") is None:
        participation_dict.pop("id", None)

    insert_result = await connector.execute("insert", {"table": TABLE, "data": participation_dict})
    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_participation = insert_result.data[0]
    return ParticipationResponse.model_validate(created_participation)


@ROUTER.patch("/{race}/participation/{identifier}", response_model=ParticipationResponse)
async def update_participation(
    body: UpdateParticipation,
    race: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
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
        raise HTTPException(status_code=404, detail="Participation not found after update")
    return ParticipationResponse.model_validate(updated.data[0])


@ROUTER.delete("/{race}/participation/{identifier}")
async def remove_participation(
    race: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Participation with ID {identifier} not found")

    update_data = {"updated_at": datetime.now(UTC)}
    result = await connector.execute(
        "update", {"table": TABLE, "data": update_data, "filters": {"id": identifier}}
    )
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't delete the object with the ID {identifier}. Traceback: {result.error}",
        )
    return {"detail": f"{identifier} deleted"}


@ROUTER.options("/participation")
async def describe_route():
    return {
        "GET": "/v1/race/{race}/participation/{identifier}",
        "DELETE": "/v1/race/{race}/participation/{identifier}",
        "PATCH": "/v1/race/{race}/participation/{identifier}",
        "POST": "/v1/race/participation",
    }
