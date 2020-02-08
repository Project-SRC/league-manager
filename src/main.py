from fastapi import FastAPI


league = FastAPI()


@league.get("/")
async def read_root():
    return {"Hello": "World"}


@league.get("/items/{item_id}")
async def read_item(item_id: int, query: str = None):
    return {"item_id": item_id, "query": query}
