"""
Defines necessary variables used across the project.

Status: Working
"""
import json
import os

from PIL import Image

from pygame import transform, display, RESIZABLE, Surface
from pygame.font import SysFont

from utils.map_utils import px_to_colordict

# import utils.map_utils as map_utils

def _updateAndInit():
    """For things needed in init and onWInowScale."""
    global map_row_lenght, tile_size, grid_start, grid_bottom, map_row_length
    # map_row_lenght
    map_row_length = int((window_w - MAP_QUEUE_W) / 280)
    if map_row_length <= 0:
        map_row_length = 1

    # tile_size
    if window_w - MENU_WIDTH >= window_h:
        tile_size = window_h / immap.size[1]
    else:
        tile_size = (window_w - MENU_WIDTH) / immap.size[0]

    tile_size = int(tile_size) if int(tile_size) >= 1 else 1

    # grid_start and grid_bottom
    grid_start = window_w - immap.size[0] * tile_size
    grid_bottom = immap.size[1] * tile_size

def init():
    """Initializes all values."""
    global COLORS, MENU_WIDTH, score_functions, MAP_QUEUE_W, window_w, window_h, STANDARD_FONT, map_queue, immap, \
          PATH_TO_MAPS, MAPCOLORS, screen, rscreen, selected_tiles
    MENU_WIDTH = 200
    MAP_QUEUE_W = 200
    PATH_TO_MAPS = os.path.realpath("..\\resources\maps")
    window_w = 1000
    window_h = 300
    score_functions = set()
    SELF_LOC = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(SELF_LOC, '../color.json')) as json_file:
        COLORS = json.load(json_file)
    # base map to be used. Consider rewriting to avoid needing this. AKA only have this declared when on main game screen
    immap = Image.open(os.path.join(SELF_LOC, "..\\resources\maps\map0.png"))
    MAPCOLORS = px_to_colordict(immap, [(0, 255, 0),(0, 0, 255),(255, 0, 255),(255, 0, 0),(0,0,0),(255, 255, 0)])
    STANDARD_FONT = SysFont('Bahnschrift SemiBold', 30)
    map_queue = []
    screen = Surface((window_w, window_h))
    rscreen = display.set_mode((window_w, window_h), RESIZABLE)
    selected_tiles = set()
    _updateAndInit()

def onWindowScale(event):
    """Updates values when the games window is scaled."""
    global screen, rscreen, window_w, window_h
    window_w, window_h = event.size
    rscreen = display.set_mode((window_w, window_h), RESIZABLE)
    screen = transform.scale(screen, (window_w, window_h))
    screen.fill(COLORS["all"]["background"])
    _updateAndInit()