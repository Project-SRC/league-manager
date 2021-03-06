import ujson as json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from src.utils.utils import verify_exists_by_id, get_object_by_id
from src.models.user.manager import Manager
from src.models.user.user import User
from src.api.user.user import get_current_active_user
from src.db.db import run
from src.service.service import get_variable

# GET - Read
# POST - Create
# PATCH - Update
# DELETE - Delete
# OPTIONS - Show Routes

# Router for the API
ROUTER = APIRouter()

# Environment Variables
DATABASE = get_variable("RDB_DB", str) or "LEAGUE"

# Global Variables
TABLE = "manager"
USER_TABLE = "user"
NOW = str(datetime.now())

# Mapping Variables
USER_MAP = ["username", "name", "email", "password", "is_manager"]
MANAGER_MAP = ["id", "password"]


async def verify_exists(manager: dict):
    operation = "filter"
    data = {"id": manager.get("id"), "deactivated_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return True
    else:
        return False


async def update_user(user_id: str, manager_id: str, remove: bool):
    user_exist = await verify_exists_by_id(user_id, DATABASE, USER_TABLE)
    if not remove:
        manager_exist = await verify_exists_by_id(manager_id, DATABASE, TABLE)
    else:
        manager_exist = True
    if user_exist and manager_exist:
        operation = "update"
        body = {"updated_at": NOW, "is_manager": not remove, "manager_id": manager_id}
        payload = {
            "database": DATABASE,
            "table": USER_TABLE,
            "identifier": user_id,
            "data": body,
        }
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=409,
                detail=f"Database couldn't update the object with the ID {user_id}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            return True
    else:
        raise HTTPException(
            status_code=403, detail=f"User or Manager doesn't exist in the database."
        )


@ROUTER.get("/{user}/manager/{identifier}", response_model=Manager)
async def get_manager(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    operation = "get"
    payload = {"database": DATABASE, "table": TABLE, "identifier": identifier}
    database_obj = await run(operation, payload)
    manager = database_obj.get("response_message")
    manager.update({"password": 64 * "*"})
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    elif (
        database_obj.get("status_code") == 200
        and Manager.parse_obj(manager).deactivated_at is not None
    ):
        raise HTTPException(
            status_code=409, detail=f"Object with ID {identifier} is deleted."
        )
    else:
        return Manager.parse_obj(manager)


@ROUTER.post("/{user}/manager/", response_model=Manager)
async def create_manager(
    manager: dict, user: str, current_user: User = Depends(get_current_active_user)
):
    user_exist = await get_object_by_id(user, DATABASE, USER_TABLE, User)
    if not user_exist:
        raise HTTPException(
            status_code=404, detail=f"User with ID {user} doesn't exist"
        )

    user_vals = json.loads(user_exist.json())
    user_vals = {key: value for key, value in user_vals.items() if key in USER_MAP}
    exists = await verify_exists(manager)
    if not exists and not user_vals.get("is_manager", False):
        operation = "insert"
        data = json.loads(Manager.parse_obj({**manager, **user_vals}).json())
        data = {key: value for key, value in data.items() if key not in MANAGER_MAP}
        fixed_id = manager.get("id", False)
        payload = {"database": DATABASE, "table": TABLE, "data": data}
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Database couldn't create the object. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            if not fixed_id:
                data.update(
                    {
                        "id": database_obj.get("response_message").get(
                            "generated_keys"
                        )[0]
                    }
                )

            data.update(
                {
                    "password": 64 * "*",
                    "is_manager": True,
                    "manager_id": data.get("id"),
                }
            )
            await update_user(user_id=user, manager_id=data.get("id"), remove=False)
            return Manager.parse_obj(data)
    else:
        raise HTTPException(status_code=403, detail=f"Manager already registered.")


@ROUTER.patch("/{user}/manager/{identifier}", response_model=Manager)
async def update_manager(
    body: dict,
    user: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    user_exist = await get_object_by_id(user, DATABASE, USER_TABLE, User)
    if not user_exist:
        raise HTTPException(
            status_code=404, detail=f"User with ID {user} doesn't exist"
        )

    user_vals = json.loads(user_exist.json())
    user_vals = {key: value for key, value in user_vals.items() if key in USER_MAP}
    exists = await get_object_by_id(identifier, DATABASE, TABLE, Manager)
    if not exists:
        operation = "update"
        body.update({"updated_at": NOW})
        payload = {
            "database": DATABASE,
            "table": TABLE,
            "identifier": identifier,
            "data": body,
        }
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Database couldn't update the object. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            manager = (
                database_obj.get("response_message").get("changes")[0].get("new_val")
            )
            manager.update({"password": 64 * "*", "is_manager": True, "manager_id": identifier})
            return Manager.parse_obj(
                database_obj.get("response_message").get("changes")[0].get("new_val")
            )
    else:
        raise HTTPException(
            status_code=403, detail=f"Manager with ID {identifier} doesn't exist."
        )


@ROUTER.delete("/{user}/manager/{identifier}")
async def remove_manager(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    # Soft remove (no data is deleted)
    user_exist = await get_object_by_id(user, DATABASE, USER_TABLE, User)
    if not user_exist:
        raise HTTPException(
            status_code=404, detail=f"User with ID {user} doesn't exist"
        )

    exists = await get_object_by_id(identifier, DATABASE, TABLE, Manager)
    if not exists:
        operation = "update"
        data = {"updated_at": NOW, "deactivated_at": NOW}
        payload = {
            "database": DATABASE,
            "table": TABLE,
            "identifier": identifier,
            "data": data,
        }
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Database couldn't delete the object. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            await update_user(user_id=user, manager_id=None, remove=True)
            return {"detail": f"{identifier} deleted"}
    else:
        raise HTTPException(
            status_code=403, detail=f"Manager with ID {identifier} doesn't exist."
        )


@ROUTER.options("/manager")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/user/{user}/manager/{identifier}",
        "DELETE": "/v1/user/{user}/manager/{identifier}",
        "PATCH": "/v1/user/{user}/manager/{identifier}",
        "POST": "/v1/user/manager",
    }
