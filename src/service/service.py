from environs import Env
from types import FunctionType

VARIABLES = [
    "MOCK",
    "TEST",
    "VERSION",
    "WS_ADDRESS",
    "WS_PORT",
    "RDB_DB",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
]


def get_variable(name: str = None, function: FunctionType = str):
    env = Env()
    env.read_env()

    for var in VARIABLES:
        env(var)

    if name not in VARIABLES:
        return None
    if name:
        return function(env.dump().get(name))
    else:
        return env.dump()
