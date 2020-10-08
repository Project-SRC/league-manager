import asyncio
import logging
import websockets
import ujson as json
from datetime import datetime
from environs import Env
from uuid import uuid4
from websockets import ConnectionClosed
from src.service.service import get_variable

# Environment Variables
WS_ADDRESS = get_variable("WS_ADDRESS", str) or "localhost"
WS_PORT = get_variable("WS_PORT", int) or 8765

# Logger
_logger = logging.getLogger(__name__)

# Rethink Data Manager - Call type
TYPE = "rethink-manager-call"


async def communicate(operation: str, payload: dict, **kwargs):
    try:
        addr = f"ws://{WS_ADDRESS}:{WS_PORT}/{operation}"
        async with websockets.connect(addr) as websocket:
            await websocket.send(json.dumps(payload))
            _logger.info(f"Message sent: {payload}")
            response = await websocket.recv()
            _logger.info(f"Message received: {response}")

            return json.loads(response)
    except (asyncio.TimeoutError) as err:
        _logger.error(
            f"Asyncio Timeout Error while trying to communicate with the database. Traceback: {err}")
    except (ConnectionRefusedError) as err:
        _logger.error(
            f"The connection with the websocket (Address: {addr}) was refused. Traceback: {err}")
    except ConnectionClosed as err:
        _logger.error(err)
    except RuntimeError as err:
        _logger.error(err)
    except Exception as err:
        _logger.error(err)


async def run(operation: str, data: dict):
    try:
        payload = {
            "id": str(uuid4()),
            "time": datetime.now().isoformat("T") + "Z",
            "type": TYPE,
            "payload": data
        }
        response = await communicate(operation, payload)
        return response
    except Exception as err:
        _logger.error(err)
