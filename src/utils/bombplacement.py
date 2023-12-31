"""
Implemnets a simple function for clearing all bombs.

Status: Working
"""


import shared
from components.bombs import Bomb


def clearBombs():
    """Clears all bombs from the map."""
    for bomb in Bomb.instances.values():
        bomb.tiles = set()
        shared.selected_tiles = set()


def placeBombs(bomb_cords: dict):
    """Takes in a dict of the form:
    {
    bomb_key : [[int, int], [int, int], ...]
    ...
    }, where [int, int] is a valid coordinate for the bomb and
    bomb_key is the same as the keys found in Bomb.instnaces

    and places the bombs on the map.
    """
    for key, value in Bomb.instances.items():
        if key in bomb_cords:
            value.tiles = {tuple(tile) for tile in bomb_cords[key]}

    shared.selected_tiles = set(
        tile for bomb in Bomb.instances.values() for tile in bomb.tiles
    )
