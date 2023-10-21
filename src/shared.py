"""
Defines necessary variables used across the project.

Status: WIP
- onWindowScale needs to be worked on
- need to change screen and rscreen to Screen type
"""
import json
import os

from PIL import Image

from pygame import transform, display, RESIZABLE
from pygame.font import SysFont

# import utils.map_utils as map_utils

def _updateAndInit():
    global map_row_lenght, tile_size
    """For things needed in init and onWInowScale."""
    # map_row_lenght
    map_row_lengh = int((window_w - MAP_QUEUE_W) / 280)
    if map_row_lengh == 0:
        map_row_lengh = 1

    # tile_size
    if window_w - MENU_WIDTH >= window_h:
        tile_size = window_h / immap.size[1]
    else:
        tile_size = (window_w - MENU_WIDTH) / immap.size[0]

    tile_size = int(tile_size) if int(tile_size) >= 1 else 1

def init():
    global colors, MENU_WIDTH, score_functions, MAP_QUEUE_W, window_w, window_h, STANDARD_FONT, map_row_lenght, map_queue, immap, PATH_TO_MAPS
    MENU_WIDTH = 200
    MAP_QUEUE_W = 200
    PATH_TO_MAPS = os.path.realpath("..\\resources\maps")
    window_w = 1000
    window_h = 300
    score_functions = set()
    SELF_LOC = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(SELF_LOC, '../color.json')) as json_file:
        colors = json.load(json_file)
    # base map to be used. Consider rewriting to avoid needing this. AKA only have this declared when on main game screen
    immap = Image.open(os.path.join(SELF_LOC, "..\\resources\maps\map0.png"))
    STANDARD_FONT = SysFont('Bahnschrift SemiBold', 30)
    map_queue = []
    _updateAndInit()

# Take closer look at this later on
def onWindowScale(event):
    window_w, window_h = event.size
    map_row_lengh = int((window_w - MAP_QUEUE_W) / 280)
    if map_row_lengh == 0:
        map_row_lengh = 1
    rscreen = display.set_mode((window_w, window_h), RESIZABLE)
    screen = transform.scale(screen, (window_w, window_h))
    screen.fill(colors["all"]["background"])
    _updateAndInit()