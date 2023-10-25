"""
Implemnets a simple function for clearing all bombs.

Status: Working
"""


from components.bombs import Bomb
import shared

def clearBombs():
    """Clears all bombs from the map."""
    for bomb in Bomb.instances.values():
        bomb.tiles = set()
        shared.selected_tiles = set()
