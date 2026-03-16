from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import CreateDriver, DriverResponse, UpdateDriver
from src.schemas.user import Driver as DriverModel

ROUTER = APIRouter()

TABLE = "driver"
USER_TABLE = "user"


async def update_user(driver_id: UUID, remove: bool):
    connector = get_connector()
    result = await connector.execute(
        "select", {"table": USER_TABLE, "filters": {"driver_id": str(driver_id)}}
    )
    if result.error:
        raise HTTPException(status_code=500, detail=f"Database error: {result.error}")

    if not result.data:
        return False

    data = {"updated_at": datetime.now(UTC), "is_driver": not remove}
    if remove:
        data["driver_id"] = None
    else:
        data["driver_id"] = str(driver_id)

    user_id = result.data[0].get("id")
    result = await connector.execute(
        "update", {"table": USER_TABLE, "data": data, "filters": {"id": user_id}}
    )
    if result.error:
        raise HTTPException(
            status_code=409,
            detail=f"Database couldn't update the object. Traceback: {result.error}",
        )
    return True


@ROUTER.get("/{user}/driver/{identifier}", response_model=DriverResponse)
async def get_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()
    result = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Traceback: {result.error}",
        )
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Driver with ID {identifier} not found")

    driver_data = result.data[0]
    if driver_data.get("deleted_at"):
        raise HTTPException(status_code=409, detail=f"Object with ID {identifier} is deleted.")

    return DriverResponse.model_validate(driver_data)


@ROUTER.post("/{user}/driver/", response_model=DriverResponse)
async def create_driver(
    driver: CreateDriver, user: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    user_result = await connector.execute("select", {"table": USER_TABLE, "filters": {"id": user}})
    if user_result.error:
        raise HTTPException(status_code=500, detail=f"Database error: {user_result.error}")
    if not user_result.data:
        raise HTTPException(status_code=404, detail=f"User with ID {user} doesn't exist")

    user_data = user_result.data[0]
    if user_data.get("is_driver") and user_data.get("driver_id"):
        raise HTTPException(status_code=403, detail="Driver already registered.")

    existing_driver = await connector.execute(
        "select", {"table": TABLE, "filters": {"user_id": str(driver.user_id)}}
    )
    if not existing_driver.data:
        raise HTTPException(status_code=403, detail="Driver already registered.")

    driver_dict = driver.model_dump()
    driver_dict["active"] = True
    driver_dict["total_podiums"] = 0
    driver_dict["total_points"] = 0
    driver_dict["total_races"] = 0
    driver_dict["championships_won"] = 0

    insert_result = await connector.execute("insert", {"table": TABLE, "data": driver_dict})
    if insert_result.error:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_driver = insert_result.data[0]
    await update_user(UUID(created_driver["id"]), remove=False)

    return DriverResponse.model_validate(created_driver)


@ROUTER.patch("/{user}/driver/{identifier}", response_model=DriverResponse)
async def update_driver(
    body: dict,
    user: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    connector = get_connector()

    user_result = await connector.execute("select", {"table": USER_TABLE, "filters": {"id": user}})
    if user_result.error:
        raise HTTPException(status_code=500, detail=f"Database error: {user_result.error}")
    if not user_result.data:
        raise HTTPException(status_code=404, detail=f"User with ID {user} doesn't exist")

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=403, detail=f"Driver with ID {identifier} doesn't exist.")

    update_data = {k: v for k, v in body.items() if v is not None}
    update_data["updated_at"] = datetime.now(UTC)

    result = await connector.execute(
        "update", {"table": TABLE, "data": update_data, "filters": {"id": identifier}}
    )
    if result.error:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't update the object. Traceback: {result.error}",
        )

    updated = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if not updated.data:
        raise HTTPException(status_code=404, detail="Driver not found after update")
    return DriverResponse.model_validate(updated.data[0])


@ROUTER.delete("/{user}/driver/{identifier}")
async def remove_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    user_result = await connector.execute("select", {"table": USER_TABLE, "filters": {"id": user}})
    if user_result.error:
        raise HTTPException(status_code=500, detail=f"Database error: {user_result.error}")
    if not user_result.data:
        raise HTTPException(status_code=404, detail=f"User with ID {user} doesn't exist")

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=403, detail=f"Driver with ID {identifier} doesn't exist.")

    update_data = {
        "updated_at": datetime.now(UTC),
        "deleted_at": datetime.now(UTC),
    }
    result = await connector.execute(
        "update", {"table": TABLE, "data": update_data, "filters": {"id": identifier}}
    )
    if result.error:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't delete the object. Traceback: {result.error}",
        )

    await update_user(UUID(identifier), remove=True)
    return {"detail": f"{identifier} deleted"}


@ROUTER.options("/driver")
async def describe_route():
    return {
        "GET": "/v1/user/{user}/driver/{identifier}",
        "DELETE": "/v1/user/{user}/driver/{identifier}",
        "PATCH": "/v1/user/{user}/driver/{identifier}",
        "POST": "/v1/user/driver",
    }
