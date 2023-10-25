"""
Implements the function responsible for selecting tiles.

Status: Working
"""
from utils.utils import cordsConvert
from components.bombs import Bomb
import shared


def selectTiles(selection, active_bomb, remove = False):
    '''Takes care of the selecting of tiles and addding/removing them to/from the selected_tiles set and the apropriate bomb set'''
    pos1, pos2 = selection
    x1, y1 = pos1
    x2, y2 = pos2
    if x2 > x1:
        x1, x2 = x2, x1
    if y2 > y1:
        y1, y2 = y2, y1
    converted_pos1 = cordsConvert((x1,y1), shared.tile_size, True)
    converted_pos2 = cordsConvert((x2,y2), shared.tile_size, True)
    if converted_pos1[0] < shared.grid_start or converted_pos1[1] >= shared.grid_bottom or converted_pos2[1] >= shared.grid_bottom:
        return active_bomb.tiles

    for x in range((x1 - x2)+1):
        x += x2
        for y in range((y1 - y2)+1):
            y += y2
            if (x,y) in shared.selected_tiles and remove == True:
                shared.selected_tiles.remove((x,y))
                if (x,y) in active_bomb.tiles:
                    active_bomb.tiles.remove((x,y))
                else:
                    for bomb in Bomb.instances.values():
                        if not (x,y) in bomb.tiles:
                            continue
                        bomb.tiles.remove((x,y))
            elif not (x,y) in shared.selected_tiles and remove == False:
                shared.selected_tiles.add((x, y))
                active_bomb.tiles.add((x,y))

    return active_bomb.tiles