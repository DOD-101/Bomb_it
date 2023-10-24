"""
Defines necessary variables used across the project.

Status: Working
"""
import json
import os

from pygame import transform, display, RESIZABLE, Surface
from pygame.font import Font

from utils.gamestage_enum import GameStage
from utils.map_utils import px_to_colordict, getAnImmap

# import utils.map_utils as map_utils

def _updateAndInit(resize = False):
    """For things needed in init and onWInowScale."""
    global map_row_lenght, tile_size, grid_start, grid_bottom, map_row_length
    # map_row_lenght
    map_row_length = int((window_w - MAP_QUEUE_W) / 280)
    if map_row_length <= 0:
        map_row_length = 1

    if stage == GameStage.GAME:
        gameVars(resize)

def init():
    """Initializes all values."""
    global COLORS, MENU_WIDTH, score_functions, MAP_QUEUE_W, window_w, window_h, STANDARD_FONT, map_queue, immap, \
          PATH_TO_MAPS, screen, rscreen, selected_tiles, stage
    MENU_WIDTH = 200
    MAP_QUEUE_W = 200
    PATH_TO_MAPS = os.path.realpath(os.path.join('..', 'assets', 'maps'))
    window_w = 1000
    window_h = 300
    score_functions = set()
    SELF_LOC = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(SELF_LOC, '..', 'assets', 'color.json')) as json_file:
        COLORS = json.load(json_file)
    STANDARD_FONT = Font(os.path.join('..', 'assets',  'fonts', 'OpenSans', 'static', 'OpenSans_Condensed-SemiBold.ttf'), 30)
    map_queue = []
    stage = GameStage.START
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
    _updateAndInit(resize=True)

def gameVars(resize = False, first = False):
    """Variables only needed in the main stage of the game"""
    global immap, mapcolors, tile_size, grid_start, grid_bottom, TILES
    if first:
        SELF_LOC = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(SELF_LOC, '..', 'assets', 'tiles.json')) as f:
            TILES = json.load(f)

    if not resize:
        immap = getAnImmap(map_queue)
        tile_colors = [tuple(TILES[key]['color']) for key in TILES]
        mapcolors = px_to_colordict(immap, tile_colors)

    # tile_size
    if window_w - MENU_WIDTH >= window_h:
        tile_size = window_h / immap.size[1]
    else:
        tile_size = (window_w - MENU_WIDTH) / immap.size[0]

    tile_size = int(tile_size) if int(tile_size) >= 1 else 1

    # grid_start and grid_bottom
    grid_start = window_w - immap.size[0] * tile_size
    grid_bottom = immap.size[1] * tile_size