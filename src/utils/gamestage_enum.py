"""
Implements the enums for different game stages.

Status: Waiting to be used.
"""

from enum import IntEnum, auto

class GameStage(IntEnum):
    QUIT = auto()
    START = auto()
    MAP_SELECT = auto()
    GAME = auto()
