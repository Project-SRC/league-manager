import asyncio
import websockets
import ujson as json
from datetime import datetime
from uuid import uuid4
from websockets import ConnectionClosed
from src.config import settings, log

TYPE = "rethink-manager-call"


async def communicate(operation: str, payload: dict, **kwargs):
    addr: str = ""
    try:
        addr = f"ws://{settings.WS_ADDRESS}:{settings.WS_PORT}/{operation}"
        async with websockets.connect(addr) as websocket:
            await websocket.send(json.dumps(payload))
            log.info("message_sent", payload=payload)
            response = await websocket.recv()
            log.info("message_received", response=response)

            return json.loads(response)
    except asyncio.TimeoutError as err:
        log.error("timeout_error", error=str(err))
    except ConnectionRefusedError as err:
        log.error("connection_refused", address=addr, error=str(err))
    except ConnectionClosed as err:
        log.error("connection_closed", error=str(err))
    except RuntimeError as err:
        log.error("runtime_error", error=str(err))
    except Exception as err:
        log.error("unexpected_error", error=str(err))


async def run(operation: str, data: dict):
    try:
        payload = {
            "id": str(uuid4()),
            "time": datetime.now().isoformat("T") + "Z",
            "type": TYPE,
            "payload": data,
        }
        response = await communicate(operation, payload)
        return response
    except Exception as err:
        log.error("run_error", error=str(err))
