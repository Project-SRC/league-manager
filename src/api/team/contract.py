import ujson as json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from environs import Env
from utils.utils import verify_id, verify_exists_by_id
from models.team.contract import Contract
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
TABLE = "contract"
TEAM_TABLE = "team"
DRIVER_TABLE = "driver"


async def verify_exists(contract: Contract):
    operation = "filter"
    data = {"driver": str(contract.driver), "deleted_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return True
    else:
        return False


@ROUTER.get("/{team}/contract/{identifier}", response_model=Contract)
async def get_contract(
    team: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    operation = "filter"
    payload = {
        "database": DATABASE,
        "table": TABLE,
        "filter": {"id": identifier, "team": team},
    }
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    elif (
        database_obj.get("status_code") == 200
        and Contract.parse_obj(database_obj.get("response_message")).deleted_at is not None
    ):
        raise HTTPException(
            status_code=409, detail=f"Object with ID {identifier} is deleted."
        )
    else:
        return Contract.parse_obj(database_obj.get("response_message"))


@ROUTER.post("/{team}/contract/", response_model=Contract)
async def create_contract(
    contract: Contract, team: str, current_user: User = Depends(get_current_active_user)
):
    team_exist = await verify_exists_by_id(team, DATABASE, TEAM_TABLE)
    if not team_exist:
        raise HTTPException(
            status_code=404, detail=f"The Team with ID {team} doesn't exist"
        )

    driver_exist = await verify_exists_by_id(
        str(contract.driver), DATABASE, DRIVER_TABLE
    )
    if not driver_exist:
        raise HTTPException(
            status_code=404,
            detail=f"The Driver with ID {contract.driver} doesn't exist",
        )

    exists = await verify_exists(contract)
    if not exists:
        operation = "insert"
        data = json.loads(contract.json())
        fixed_id = verify_id(contract)
        if fixed_id:
            database_obj = await run(operation, data)
        else:
            data.pop("id")

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
            return Contract.parse_obj(data)
    else:
        raise HTTPException(
            status_code=403, detail=f"Driver already have a contract running."
        )


@ROUTER.patch("/{team}/contract/{identifier}", response_model=Contract)
async def update_contract(
    body: dict,
    team: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    # TODO: Verify if the team is the correct one for the contract
    exist = await verify_exists_by_id(identifier, DATABASE, TABLE)
    if exist:
        operation = "update"
        now = str(datetime.now())
        body.update({"updated_at": now})
        payload = {
            "database": DATABASE,
            "table": TABLE,
            "identifier": identifier,
            "data": body,
        }
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=409,
                detail=f"Database couldn't update the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            return Contract.parse_obj(
                database_obj.get("response_message").get("changes")[0].get("new_val")
            )
    else:
        raise HTTPException(status_code=403, detail=f"Object not found on database.")


@ROUTER.delete("/{team}/contract/{identifier}")
async def remove_contract(
    team: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    operation = "update"
    now = str(datetime.now())
    data = {}
    data.update({"updated_at": now})
    data.update({"terminated_at": now})
    payload = {
        "database": DATABASE,
        "table": TABLE,
        "identifier": identifier,
        "data": data,
    }
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't delete the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    else:
        return {"detail": f"{identifier} deleted"}


@ROUTER.options("/contract")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/team/{team}/contract/{identifier}",
        "DELETE": "/v1/team/{team}/contract/{identifier}",
        "PATCH": "/v1/team/{team}/contract/{identifier}",
        "POST": "/v1/team/contract",
    }
