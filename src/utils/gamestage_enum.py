"""
Implements the enums for different game stages.

Status: Working
"""

from enum import IntEnum, auto


class GameStage(IntEnum):
    """Contains the enums for different game stages."""

    QUIT = auto()
    START = auto()
    MAP_SELECT = auto()
    SCORE = auto()
    GAME = auto()
