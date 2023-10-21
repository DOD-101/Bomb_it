
from utils import cordsConvert
from components.bombs import Bomb


def selectTiles(selected_tiles, active_bomb, grid_start, grid_bottom):
    '''Takes care of the selecting of tiles and addding/removing them to/from the selected_tiles set and the apropriate bomb set'''
    global selection
    pos1, pos2 = selection
    x1, y1 = pos1
    x2, y2 = pos2
    if x2 > x1:
        x1, x2 = x2, x1
    if y2 > y1:
        y1, y2 = y2, y1
    converted_pos1 = cordsConvert((x1,y1), True)
    converted_pos2 = cordsConvert((x2,y2), True)
    if converted_pos1[0] < grid_start or converted_pos1[1] >= grid_bottom or converted_pos2[1] >= grid_bottom:
        return None
    for x in range((x1 - x2)+1):
        x += x2
        for y in range((y1 - y2)+1):
            y += y2
            if (x,y) in selected_tiles:
                selected_tiles.remove((x,y))
                if (x,y) in active_bomb.tiles:
                    active_bomb.tiles.remove((x,y))
                else:
                    for bomb in Bomb.instances.values():
                        if not (x,y) in bomb.tiles:
                            continue
                        bomb.tiles.remove((x,y))
            else:
                selected_tiles.add((x, y))
                active_bomb.tiles.add((x,y))