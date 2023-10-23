"""
Implements the Bomb abc and the conventional bomb.

Status: Working
"""
import abc

from pygame import Surface, Rect, draw, transform

import shared
from utils.utils import strToRGB, cordsConvert
from .buttons import BombButton

class Bomb(abc.ABC):
    '''This is the abc that all bombs should inherit from'''
    instances = {}
    explode_durations = []
    def __init__(self, surface: Surface, radius, explode_duration, tile_icon: tuple | Surface, explosion_color, key:str, nickname:str, price:int, create_button = True, buttonname = "NONE") -> None:
        self.surface = surface
        self.key = key
        self.nickname = nickname
        self.radius = radius
        if type(tile_icon) == str:
            self.tile_icon = strToRGB(tile_icon)
        else:
            self.tile_icon = tile_icon
        self.tiles = set()
        self.explode_duration = explode_duration
        self.explosion_color = explosion_color
        self.price = price
        if create_button:
            BombButton(surface, buttonname,0,0,0,0, self.nickname, self) # should be changed to make it clear that a BombButton is being made when setting the create button arg

        # Bomb.instances[self.instance_name] = [self.__class__.__name__, self.instance_name,self.nickname]
        Bomb.explode_durations.append(self.explode_duration)

    def setSurface(self, surface):
        """Updated the self.surface variable of the bomb"""
        self.surface = surface

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def calculateAreas(self):
        pass

    @abc.abstractmethod
    def explode(self):
        pass

class ConventionalBomb(Bomb):
    def __init__(self, screen, radius, explode_duration, tile_icon: tuple | Surface, key:str, nickname:str, price: int) -> None:
        super().__init__(screen, radius, explode_duration, tile_icon, shared.COLORS["game"]["bombs"]["conventional"]["explosion-area"], key, nickname, price, create_button=True, buttonname=key)

    def draw(self):
        if type(self.tile_icon) == tuple:
            for loc in self.tiles:
                real_loc = cordsConvert(loc, shared.tile_size, True)
                rect = Rect(real_loc[0], real_loc[1], shared.tile_size, shared.tile_size)
                draw.rect(self.surface, self.tile_icon, rect)
        elif type(self.tile_icon) == Surface:
            for loc in self.tiles:
                real_loc = cordsConvert(loc, shared.tile_size, True)
                tile_icon_scaled = transform.scale(self.tile_icon, (shared.tile_size, shared.tile_size))
                self.surface.blit(tile_icon_scaled, (real_loc[0], real_loc[1]))
        else:
            raise TypeError(f"Invalid type '{type(self.tile_icon)}' for self.tile_icon")

    def calculateAreas(self):
        """This bomb type has only 1 Area: explosion_area"""
        self.explosion_area: set[tuple[int,int]] = set()
        for loc in self.tiles:
            rect = [loc[0] - self.radius, loc[1] - self.radius, loc[0] + self.radius, loc[1] + self.radius] #not a pygame rect! [top_left_x, top_left_y, bottom_right_x, bottom_right_y]
            for x in range(rect[0], rect[2] + 1):
                for y in range(rect[1], rect[3] + 1):
                    self.explosion_area.add((x,y))

    def explode(self, current_t, explode_t):
        if not current_t - self.explode_duration <= explode_t or self.tiles == set():
            return None
        for explosion_effect in self.explosion_area:
            real_loc = cordsConvert(explosion_effect, shared.tile_size, True)
            draw.rect(self.surface, self.explosion_color, Rect(real_loc[0], real_loc[1],shared.tile_size,shared.tile_size))
