from . import participation, race
from .participation import ROUTER as PARTICIPATION_ROUTER
from .race import ROUTER as RACE_ROUTER

__all__ = ["participation", "race", "RACE_ROUTER", "PARTICIPATION_ROUTER"]
