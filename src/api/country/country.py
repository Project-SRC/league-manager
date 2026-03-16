from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.db import get_connector
from src.models.user.user import User
from src.schemas.pydantic import CountryResponse, CreateCountry, UpdateCountry

ROUTER = APIRouter()

TABLE = "country"


@ROUTER.get("/{identifier}", response_model=CountryResponse)
async def get_country(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()
    result = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if result.error:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Traceback: {result.error}",
        )
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Country with ID {identifier} not found")

    country_data = result.data[0]
    if country_data.get("deleted_at"):
        raise HTTPException(status_code=409, detail=f"Object with ID {identifier} is deleted.")

    return CountryResponse.model_validate(country_data)


@ROUTER.post("/", response_model=CountryResponse)
async def create_country(
    country: CreateCountry, current_user: User = Depends(get_current_active_user)
):
    connector = get_connector()

    country_dict = country.model_dump()
    if country_dict.get("id") is None:
        country_dict.pop("id", None)

    insert_result = await connector.execute("insert", {"table": TABLE, "data": country_dict})
    if insert_result.error or not insert_result.data:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Traceback: {insert_result.error}",
        )

    created_country = insert_result.data[0]
    return CountryResponse.model_validate(created_country)


@ROUTER.patch("/{identifier}", response_model=CountryResponse)
async def update_country(
    body: UpdateCountry, identifier: str, current_user: User = Depends(get_current_active_user)
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
        raise HTTPException(status_code=404, detail="Country not found after update")
    return CountryResponse.model_validate(updated.data[0])


@ROUTER.delete("/{identifier}")
async def remove_country(identifier: str, current_user: User = Depends(get_current_active_user)):
    connector = get_connector()

    existing = await connector.execute("select", {"table": TABLE, "filters": {"id": identifier}})
    if existing.error:
        raise HTTPException(status_code=500, detail=f"Database error: {existing.error}")
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Country with ID {identifier} not found")

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
        "GET": "/v1/country/{identifier}",
        "DELETE": "/v1/country/{identifier}",
        "PATCH": "/v1/country/{identifier}",
        "POST": "/v1/country/",
    }
