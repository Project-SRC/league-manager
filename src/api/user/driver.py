import ujson as json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from environs import Env
from utils.utils import verify_exists_by_id, get_object_by_id
from models.user.driver import Driver
from models.user.user import User
from api.user.user import get_current_active_user
from db.db import run
from service.service import get_variable

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
TABLE = "driver"
USER_TABLE = "user"
NOW = str(datetime.now())

# Mapping Variables
USER_MAP = ["username", "name", "email", "password", "is_driver"]
DRIVER_MAP = ["id", "password"]


async def verify_exists(driver: dict):
    operation = "filter"
    data = {"id": driver.get("id"), "deleted_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return True
    else:
        return False


async def update_user(user_id: str, driver_id: str, remove: bool):
    user_exist = await verify_exists_by_id(user_id, DATABASE, USER_TABLE)
    if not remove:
        driver_exist = await verify_exists_by_id(driver_id, DATABASE, TABLE)
    else:
        driver_exist = True
    if user_exist and driver_exist:
        operation = "update"
        body = {"updated_at": NOW, "is_driver": not remove, "driver_id": driver_id}
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
            status_code=403, detail=f"User or Driver doesn't exist in the database."
        )


@ROUTER.get("/{user}/driver/{identifier}", response_model=Driver)
async def get_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    operation = "get"
    payload = {"database": DATABASE, "table": TABLE, "identifier": identifier}
    database_obj = await run(operation, payload)
    driver = database_obj.get("response_message")
    driver.update({"password": 64 * "*"})
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    elif (
        database_obj.get("status_code") == 200
        and Driver.parse_obj(driver).deleted_at is not None
    ):
        raise HTTPException(
            status_code=409, detail=f"Object with ID {identifier} is deleted."
        )
    else:
        return Driver.parse_obj(driver)


@ROUTER.post("/{user}/driver/", response_model=Driver)
async def create_driver(
    driver: dict, user: str, current_user: User = Depends(get_current_active_user)
):
    user_exist = await get_object_by_id(user, DATABASE, USER_TABLE, User)
    if not user_exist:
        raise HTTPException(
            status_code=404, detail=f"User with ID {user} doesn't exist"
        )

    user_vals = json.loads(user_exist.json())
    user_vals = {key: value for key, value in user_vals.items() if key in USER_MAP}
    exists = await verify_exists(driver)
    if not exists and not user_vals.get("is_driver", False):
        operation = "insert"
        data = json.loads(Driver.parse_obj({**driver, **user_vals}).json())
        data = {key: value for key, value in data.items() if key not in DRIVER_MAP}
        fixed_id = driver.get("id", False)
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
                {"password": 64 * "*", "is_driver": True, "driver_id": data.get("id")}
            )
            await update_user(user_id=user, driver_id=data.get("id"), remove=False)
            return Driver.parse_obj(data)
    else:
        raise HTTPException(status_code=403, detail=f"Driver already registered.")


@ROUTER.patch("/{user}/driver/{identifier}", response_model=Driver)
async def update_driver(
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
    exists = await get_object_by_id(identifier, DATABASE, TABLE, Driver)
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
            driver = (
                database_obj.get("response_message").get("changes")[0].get("new_val")
            )
            driver.update(
                {"password": 64 * "*", "is_driver": True, "driver_id": identifier}
            )
            return Driver.parse_obj(
                database_obj.get("response_message").get("changes")[0].get("new_val")
            )
    else:
        raise HTTPException(
            status_code=403, detail=f"Driver with ID {identifier} doesn't exist."
        )


@ROUTER.delete("/{user}/driver/{identifier}")
async def remove_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    # Soft remove (no data is deleted)
    user_exist = await get_object_by_id(user, DATABASE, USER_TABLE, User)
    if not user_exist:
        raise HTTPException(
            status_code=404, detail=f"User with ID {user} doesn't exist"
        )

    exists = await get_object_by_id(identifier, DATABASE, TABLE, Driver)
    if not exists:
        operation = "update"
        data = {"updated_at": NOW, "deleted_at": NOW}
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
            await update_user(user_id=user, driver_id=None, remove=True)
            return {"detail": f"{identifier} deleted"}
    else:
        raise HTTPException(
            status_code=403, detail=f"Driver with ID {identifier} doesn't exist."
        )


@ROUTER.options("/driver")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/user/{user}/driver/{identifier}",
        "DELETE": "/v1/user/{user}/driver/{identifier}",
        "PATCH": "/v1/user/{user}/driver/{identifier}",
        "POST": "/v1/user/driver",
    }
