
import abc

from pygame import Surface, Rect, draw, transform

from shared import colors, tile_size
from utils.utils import strToRGB, cordsConvert
from buttons import BombButton

class Bomb(abc.ABC):
    '''This is the abc that all bombs should inherit from'''
    instances = {}
    explode_durations = []
    def __init__(self, screen: Surface, radius, explode_duration, tile_icon: tuple | Surface, explosion_color, key:str, nickname:str, create_button = True) -> None:
        self.screen = screen
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
        if create_button:
            BombButton.instances[key] = BombButton(0,0,0,0, self.nickname, self)

        # Bomb.instances[self.instance_name] = [self.__class__.__name__, self.instance_name,self.nickname]
        Bomb.explode_durations.append(self.explode_duration)

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
    def __init__(self, screen, radius, explode_duration, tile_icon: tuple | Surface, key:str, nickname:str) -> None:
        super().__init__(screen, radius, explode_duration, tile_icon, colors["game"]["bombs"]["conventional"]["explosion-area"], key, nickname)

    def draw(self):
        if type(self.tile_icon) == tuple:
            for loc in self.tiles:
                real_loc = cordsConvert(loc, True)
                rect = Rect(real_loc[0], real_loc[1], tile_size, tile_size)
                draw.rect(self.screen, self.tile_icon, rect)
        elif type(self.tile_icon) == Surface:
            for loc in self.tiles:
                real_loc = cordsConvert(loc, True)
                tile_icon_scaled = transform.scale(self.tile_icon, (tile_size, tile_size))
                self.screen.blit(tile_icon_scaled, (real_loc[0], real_loc[1]))
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
            real_loc = cordsConvert(explosion_effect, True)
            draw.rect(self.screen, self.explosion_color, Rect(real_loc[0], real_loc[1],tile_size,tile_size))
