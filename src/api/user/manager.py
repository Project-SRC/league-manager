from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import CreateManager, ManagerResponse

ROUTER = APIRouter()

TABLE = "manager"
USER_TABLE = "user"


async def update_user(manager_id: UUID, remove: bool):
    connector = get_connector()
    result = await connector.execute(
        "select", {"table": USER_TABLE, "filters": {"manager_id": str(manager_id)}}
    )
    if result.error:
        raise HTTPException(status_code=500, detail=f"Database error: {result.error}")

    if not result.data:
        return False

    data = {"updated_at": datetime.now(UTC), "is_manager": not remove}
    if remove:
        data["manager_id"] = None
    else:
        data["manager_id"] = str(manager_id)

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


@ROUTER.get("/{user}/manager/{identifier}", response_model=ManagerResponse)
async def get_manager(
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
        raise HTTPException(status_code=404, detail=f"Manager with ID {identifier} not found")

    manager_data = result.data[0]
    if manager_data.get("deactivated_at"):
        raise HTTPException(status_code=409, detail=f"Object with ID {identifier} is deactivated.")

    return ManagerResponse.model_validate(manager_data)


@ROUTER.post("/{user}/manager/", response_model=ManagerResponse)
async def create_manager(
    manager: CreateManager, user: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    user_result = await connector.execute("select", {"table": USER_TABLE, "filters": {"id": user}})
    if user_result.error:
        raise HTTPException(status_code=500, detail=f"Database error: {user_result.error}")
    if not user_result.data:
        raise HTTPException(status_code=404, detail=f"User with ID {user} doesn't exist")

    user_data = user_result.data[0]
    if user_data.get("is_manager") and user_data.get("manager_id"):
        raise HTTPException(status_code=403, detail="Manager already registered.")

    existing_manager = await connector.execute(
        "select", {"table": TABLE, "filters": {"user_id": str(manager.user_id)}}
    )
    if existing_manager.data:
        raise HTTPException(status_code=403, detail="Manager already registered.")

    manager_dict = manager.model_dump()
    manager_dict["active"] = True

    insert_result = await connector.execute("insert", {"table": TABLE, "data": manager_dict})
    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_manager = insert_result.data[0]
    await update_user(UUID(created_manager["id"]), remove=False)

    return ManagerResponse.model_validate(created_manager)


@ROUTER.patch("/{user}/manager/{identifier}", response_model=ManagerResponse)
async def update_manager(
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
        raise HTTPException(status_code=403, detail=f"Manager with ID {identifier} doesn't exist.")

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
        raise HTTPException(status_code=404, detail="Manager not found after update")
    return ManagerResponse.model_validate(updated.data[0])


@ROUTER.delete("/{user}/manager/{identifier}")
async def remove_manager(
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
        raise HTTPException(status_code=403, detail=f"Manager with ID {identifier} doesn't exist.")

    update_data = {
        "updated_at": datetime.now(UTC),
        "deactivated_at": datetime.now(UTC),
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


@ROUTER.options("/manager")
async def describe_route():
    return {
        "GET": "/v1/user/{user}/manager/{identifier}",
        "DELETE": "/v1/user/{user}/manager/{identifier}",
        "PATCH": "/v1/user/{user}/manager/{identifier}",
        "POST": "/v1/user/manager",
    }
