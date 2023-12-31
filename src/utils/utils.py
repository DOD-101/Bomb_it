"""
Implements general-use functions.

Status: Working
- cordsConvvert should just get the tile_size from shared.
"""

import typing

from pygame.mouse import get_pos as pyget_mouse_pos

import shared


def center(
    item_width: float | int = 0,
    item_height: float | int = 0,
    parent_width: float | int = 0,
    parent_height: float | int = 0,
    center_direction: typing.Literal["horizontal", "vertical", "both"] = "both",
):
    """Centers an item within "parent\" item."""

    def horizontal():
        return (parent_width - item_width) / 2

    def vertical():
        return (parent_height - item_height) / 2

    match (center_direction):
        case ("horizontal"):
            return horizontal()
        case ("vertical"):
            return vertical()
        case ("both"):
            return (horizontal(), vertical())
        case (_):
            raise ValueError(
                f"{center_direction} is an invalid value for center_direction"
            )


def getTileSize(window_w, window_h, immap):
    """
    Calculates the tile size.
    Tries to allways maximise the tile size without the grid growing past the window.
    """
    if window_w - shared.MENU_WIDTH >= window_h:
        tile_size = window_h / immap.size[1]
    else:
        tile_size = (window_w - shared.MENU_WIDTH) / immap.size[0]

    tile_size = int(tile_size) if int(tile_size) >= 1 else 1
    return tile_size


def cordsConvert(
    cord: set | list | tuple,
    tile_size,
    to_normal: bool = False,
):
    """
    If to_normal is False will convert given cordinates to tile-cords,
    otherwise it will do the reverse. Read notes on reverse.
    """
    new_cord = []
    cord_type = type(cord)
    cord_list = []
    for check in cord:
        if isinstance(check, int):
            cord_list.append(cord)
            cord = cord_list
            break
    if to_normal:
        # Does not give exact location of mouse, but rather
        # starting location of tile (aka. top left corner).
        # Unless provided tile cords are acurrate floates.
        for c in cord:
            c_type = type(c)
            c_clone = list(c)
            c_clone[0] = (c_clone[0] * tile_size) + shared.grid_start
            c_clone[1] = c_clone[1] * tile_size
            c_clone = c_type(c_clone)
            new_cord.append(c_clone)
    elif not to_normal:
        for c in cord:
            c_type = type(c)
            c_clone = list(c)
            c_clone[0] = int((c_clone[0] - shared.grid_start) / tile_size)
            c_clone[1] = int(c_clone[1] / tile_size)
            c_clone = c_type(c_clone)
            new_cord.append(c_clone)
    else:
        raise ValueError("Invalid value for to_normal!")

    new_cord = cord_type(new_cord[0])
    return new_cord


def mouseTilecords():
    """Gets the position of the mouse and converts it to tile-cordinates"""
    mouse_pos = pyget_mouse_pos()
    if mouse_pos[0] < shared.grid_start:
        mouse_tile_cords = [0, 0]
    mouse_tile_cords = cordsConvert(mouse_pos, shared.tile_size)
    return mouse_tile_cords


def strToRGB(color_str: str) -> tuple:
    """Used to convert a color Name to an RGB value. AVOID USE. WILL BE DEPRECEATED."""
    if isinstance(color_str, str):
        color_str = color_str.lower()
        match color_str:
            case ("white"):
                color_str = (255, 255, 255)
            case ("black"):
                color_str = (0, 0, 0)
            case ("red"):
                color_str = (255, 0, 0)
            case ("green"):
                color_str = (0, 255, 0)
            case ("blue"):
                color_str = (0, 0, 255)
            case ("armygreen"):
                color_str = (75, 83, 32)
            case ("explosionorange"):
                color_str = (255, 102, 0)
            case (_):
                raise ValueError(f"Color str:{color_str} doesn't exist!")
    return color_str
