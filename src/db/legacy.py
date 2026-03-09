from datetime import datetime
from typing import Any
from uuid import uuid4

import ujson as json
import websockets
from websockets import ConnectionClosed

from src.config import log, settings
from src.db.db import DBConnector
from src.models.internal.database import QueryResult

TYPE = "rethink-manager-call"


class LegacyConnector(DBConnector):
    """Legacy RethinkDB connector via websocket."""

    async def execute(self, operation: str, payload: dict[str, Any]) -> QueryResult:
        """Execute operation via legacy websocket."""
        try:
            response = await run(operation, payload)
            return QueryResult(data=[response] if response else [], count=1)
        except Exception as e:
            log.error("legacy_execute_error", operation=operation, error=str(e))
            return QueryResult(error={"message": str(e)})


async def communicate(operation: str, payload: dict[str, Any], **kwargs: dict[str, Any]):
    addr: str = ""
    try:
        addr = f"ws://{settings.WS_ADDRESS}:{settings.WS_PORT}/{operation}"
        async with websockets.connect(addr) as websocket:
            await websocket.send(json.dumps(payload))
            log.info("message_sent", payload=payload)
            response = await websocket.recv()
            log.info("message_received", response=response)
            return json.loads(response)
    except TimeoutError as err:
        log.error("timeout_error", error=str(err))
    except ConnectionRefusedError as err:
        log.error("connection_refused", address=addr, error=str(err))
    except ConnectionClosed as err:
        log.error("connection_closed", error=str(err))
    except RuntimeError as err:
        log.error("runtime_error", error=str(err))
    except Exception as err:
        log.error("unexpected_error", error=str(err))


async def run(operation: str, data: dict[str, Any]):
    try:
        payload: dict[str, Any] = {
            "id": str(uuid4()),
            "time": datetime.now().isoformat("T") + "Z",
            "type": TYPE,
            "payload": data,
        }
        response = await communicate(operation, payload)
        return response
    except Exception as err:
        log.error("run_error", error=str(err))
