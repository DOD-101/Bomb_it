"""
Implements the enums for different game stages.

Status: Working
"""

from enum import IntEnum, auto

class GameStage(IntEnum):
    QUIT = auto()
    START = auto()
    MAP_SELECT = auto()
    GAME = auto()
