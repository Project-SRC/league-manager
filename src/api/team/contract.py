from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import ContractResponse, CreateContract

ROUTER = APIRouter()

TABLE = "contract"
TEAM_TABLE = "team"
DRIVER_TABLE = "driver"


@ROUTER.get("/{team}/contract/{identifier}", response_model=ContractResponse)
async def get_contract(
    team: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()
    result = await connector.execute(
        "select", {"table": TABLE, "filters": {"id": identifier, "team_id": team}}
    )
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Traceback: {result.error}",
        )
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Contract with ID {identifier} not found")

    return ContractResponse.model_validate(result.data[0])


@ROUTER.post("/{team}/contract/", response_model=ContractResponse)
async def create_contract(
    contract: CreateContract, team: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    team_result = await connector.execute("select", {"table": TEAM_TABLE, "filters": {"id": team}})
    if team_result.error or not team_result.data:
        raise HTTPException(status_code=404, detail=f"The Team with ID {team} doesn't exist")

    driver_result = await connector.execute(
        "select", {"table": DRIVER_TABLE, "filters": {"id": str(contract.driver_id)}}
    )
    if driver_result.error or not driver_result.data:
        raise HTTPException(
            status_code=404,
            detail=f"The Driver with ID {contract.driver_id} doesn't exist",
        )

    existing = await connector.execute(
        "select",
        {"table": TABLE, "filters": {"driver_id": str(contract.driver_id), "terminated_at": None}},
    )
    if existing.data:
        raise HTTPException(status_code=403, detail="Driver already have a contract running.")

    contract_dict = contract.model_dump()
    if contract_dict.get("id") is None:
        contract_dict.pop("id", None)

    insert_result = await connector.execute("insert", {"table": TABLE, "data": contract_dict})
    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_contract = insert_result.data[0]
    return ContractResponse.model_validate(created_contract)


@ROUTER.patch("/{team}/contract/{identifier}", response_model=ContractResponse)
async def update_contract(
    body: dict,
    team: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
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
        raise HTTPException(status_code=404, detail="Contract not found after update")
    return ContractResponse.model_validate(updated.data[0])


@ROUTER.delete("/{team}/contract/{identifier}")
async def remove_contract(
    team: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Contract with ID {identifier} not found")

    update_data = {
        "updated_at": datetime.now(UTC),
        "terminated_at": datetime.now(UTC),
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


@ROUTER.options("/contract")
async def describe_route():
    return {
        "GET": "/v1/team/{team}/contract/{identifier}",
        "DELETE": "/v1/team/{team}/contract/{identifier}",
        "PATCH": "/v1/team/{team}/contract/{identifier}",
        "POST": "/v1/team/contract",
    }
