"""
Implements the function responsible for selecting tiles.

Status: Working
"""

import shared
from components.bombs import Bomb
from utils.utils import cordsConvert


def selectTiles(selection, active_bomb, remove=False):
    """
    Takes care of the selecting of tiles and adding/removing them
    to/from the selected_tiles set and the appropriate bomb set
    """
    pos1, pos2 = selection
    x1, y1 = pos1
    x2, y2 = pos2
    converted_pos1 = cordsConvert((x1, y1), shared.tile_size, True)
    converted_pos2 = cordsConvert((x2, y2), shared.tile_size, True)
    if (
        converted_pos1[0] < shared.grid_start
        or converted_pos1[1] >= shared.grid_bottom
        or converted_pos2[1] >= shared.grid_bottom
    ):
        return active_bomb.tiles

    for x in range(abs(x1 - x2) + 1):
        x += min(x1, x2)
        for y in range(abs(y1 - y2) + 1):
            y += min(y1, y2)
            tile = (x, y)
            if tile in shared.selected_tiles and remove:
                shared.selected_tiles.remove(tile)
                # active_bomb.tiles.discard(tile)
                for bomb in Bomb.instances.values():
                    try:
                        bomb.tiles.remove(tile)
                    except KeyError:
                        print(f"{bomb.key} could not remove {tile} from {bomb.tiles}")
            elif tile not in shared.selected_tiles and not remove:
                shared.selected_tiles.add(tile)
                active_bomb.tiles.add(tile)

    return active_bomb.tiles
