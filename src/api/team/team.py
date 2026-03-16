from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import CreateTeam, TeamResponse

ROUTER = APIRouter()

TABLE = "team"


@ROUTER.get("/{identifier}", response_model=TeamResponse)
async def get_team(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()
    result = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Traceback: {result.error}",
        )
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Team with ID {identifier} not found")

    team_data = result.data[0]
    if team_data.get("deleted_at"):
        raise HTTPException(status_code=409, detail=f"Object with ID {identifier} is deleted.")

    return TeamResponse.model_validate(team_data)


@ROUTER.post("/", response_model=TeamResponse)
async def create_team(team: CreateTeam, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"name": team.name}})
    if existing.data:
        raise HTTPException(status_code=403, detail="Object already exists on database.")

    team_dict = team.model_dump()
    if team_dict.get("id") is None:
        team_dict.pop("id", None)

    insert_result = await connector.execute("insert", {"table": TABLE, "data": team_dict})
    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_team = insert_result.data[0]
    return TeamResponse.model_validate(created_team)


@ROUTER.patch("/{identifier}", response_model=TeamResponse)
async def update_team(
    body: dict, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=403, detail="Object not found on database.")

    update_data = {k: v for k, v in body.items() if v is not None}
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
        raise HTTPException(status_code=404, detail="Team not found after update")
    return TeamResponse.model_validate(updated.data[0])


@ROUTER.delete("/{identifier}")
async def remove_team(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Team with ID {identifier} not found")

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
        "GET": "/v1/team/{identifier}",
        "DELETE": "/v1/team/{identifier}",
        "PATCH": "/v1/team/{identifier}",
        "POST": "/v1/team/",
    }
