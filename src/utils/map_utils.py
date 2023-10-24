"""
Implements 3 functions for working with map images.

Status: Working
"""

import os
from random import randint
from re import search

from PIL import Image


def getAnImmap(map_queue) -> Image:
    """Returns an Image to act as the map for the game."""
    if len(map_queue) != 0:
        file_name = map_queue[0].rpartition('_')[0] + ".png"
    else:
        possible_maps = []
        for current_map in  os.listdir(os.path.join('..', 'assets', 'maps')):
            file_ending = search(r".*(\..*)$", current_map).group(1)
            if not file_ending == ".png":
                continue
            possible_maps.append(current_map)
        file_name = possible_maps[randint(0, len(possible_maps) - 1)]

    return Image.open(os.path.join('..', 'assets', 'maps', file_name))


def convert_dir_to_rgb(dir: str, make_copy: bool = True, convert_all: bool = False) -> None:
    """Converts all .png files in a dir to use the RGB color mode.
    dir must be an absolute path.
    If make_copy is set to False it will simply override all the files otherwise it will make a copy with the filename prefixed by "rgb_\"
    If convert_all is set to True it will convert all images, including those which are already RGB.
    """
    for filename in os.listdir(dir):
        if filename.endswith(".png"):
            with Image.open(os.path.join(dir, filename)) as img:
                if not img.mode == "RGB" or convert_all:
                    rgb_image = img.convert("RGB")
                    # Save the converted image
                    if make_copy:
                        rgb_image.save(os.path.join(dir, f"rgb_{filename}"))
                    else:
                        rgb_image.save(os.path.join(dir, f"{filename}"))

def px_to_colordict(image: Image.Image, allowed_colors: list | set = None) -> dict:
    """Return a dict with the keys being the color and each keys value being a set with the cords of all pixels that have that color.
    If allowed_colors is left as None all colors will be allowed, otherwise only colors which have one of those values will be added.
    All values entered and returned must be/are RGB."""
    image = image.convert("RGB")
    px = image.load()

    colordict = {}
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if px[x,y] in allowed_colors or allowed_colors == None:
                if px[x,y] in colordict.keys():
                    colordict[px[x,y]].add((x,y))
                else:
                    colordict[px[x,y]] = set((x,y))

    return colordict

