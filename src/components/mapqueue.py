from random import randint
from re import search
from os import listdir, path
from uuid import uuid4
from utils import map_utils

class MapQueue(list):
    def appendMap(self, __object: any) -> None:
        """Appends a map."""
        __object = f"{__object}_{uuid4()}"
        return super().append(__object)

    def nextMap(self, gen = True) -> any:
        """Delets the current map and gets the next one or generates one. (unless gen = False)"""
        if len(self) != 0:
            del self[0]

        if len(self) == 0 and gen == True:
            self.appendRandomMap()
        elif len(self) == 0 and gen == False:
            raise ValueError(f"Cannot get next Map, because len(self) == {len(self)}")

        map_utils.getAnImmap(self)

    def appendRandomMap(self):
        """Appends a random map."""

        possible_maps = []
        for current_map in listdir(path.join('..', 'assets', 'maps')):
            file_ending = search(r".*(\..*)$", current_map).group(1)
            if not file_ending == ".png":
                continue
            current_map = current_map.removesuffix(".png")
            possible_maps.append(current_map)

        final_map = possible_maps[randint(0, len(possible_maps) - 1)]
        self.appendMap(final_map)
