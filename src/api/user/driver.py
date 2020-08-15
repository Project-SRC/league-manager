import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id, get_object_by_id
from src.models.user.driver import Driver
from src.models.user.user import User
from src.api.user.user import get_current_active_user
from src.db.db import run
from uuid import uuid4 as uuid

# GET - Read
# POST - Create
# PATCH - Update
# DELETE - Delete
# OPTIONS - Show Routes

# Router for the API
ROUTER = APIRouter()

# Environment Variables
env = Env()
env.read_env()
DATABASE = env.str("RDB_DB", default="LEAGUE")

# Global Variables
TABLE = "driver"
USER_TABLE = "user"

# Mapping Variables
USER_MAP = ["username", "name", "email"]


async def verify_exists(driver: dict):
    operation = "filter"
    data = {"id": driver.get("id"), "deleted_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return True
    else:
        return False

async def update_user(user_id: str):
    pass

@ROUTER.get("/{user}/driver/{identifier}", response_model=Driver)
async def get_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    operation = "get"
    payload = {"database": DATABASE, "table": TABLE, "identifier": identifier}
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    elif (
        database_obj.get("status_code") == 200
        and Driver.parse_obj(database_obj.get("response_message")).deleted_at != None
    ):
        raise HTTPException(
            status_code=409, detail=f"Object with ID {identifier} is deleted."
        )
    else:
        return Driver.parse_obj(database_obj.get("response_message"))


@ROUTER.post("/{user}/driver/", response_model=Driver)
async def create_driver(
    driver: dict, user: str, current_user: User = Depends(get_current_active_user)
):
    user_exist = await get_object_by_id(user, DATABASE, USER_TABLE, User)
    if not user_exist:
        raise HTTPException(
            status_code=404, detail=f"User with ID {user} doesn't exits"
        )

    user_vals = json.loads(user_exist.json())
    user_vals = {key: value for key, value in user_vals.items() if key in USER_MAP}
    exists = await verify_exists(driver)
    if not exists:
        operation = "insert"
        data = {**driver, **user_vals}
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
                data.update({"password": 64 * "*"})
            # TODO: Update User
            return Driver.parse_obj(data)
    else:
        raise HTTPException(
            status_code=403, detail=f"Driver already registered."
        )


@ROUTER.patch("/{user}/driver/{identifier}", response_model=Driver)
async def update_driver(
    body: dict,
    user: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    pass


@ROUTER.delete("/{user}/driver/{identifier}")
async def remove_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.options("/driver")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/user/{user}/driver/{identifier}",
        "DELETE": "/v1/user/{user}/driver/{identifier}",
        "PATCH": "/v1/user/{user}/driver/{identifier}",
        "POST": "/v1/user/driver",
    }
