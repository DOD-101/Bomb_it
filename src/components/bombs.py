"""
Implements the Bomb abc and the conventional bomb.

Status: Working
"""
import abc
from os.path import join
from random import randint

from pygame import Rect, Surface, draw, transform

import shared
from utils.utils import cordsConvert, strToRGB

from .buttons import BombButton


class Bomb(abc.ABC):
    """This is the abc that all bombs should inherit from"""

    instances = {}
    explode_durations = []

    def __init__(
        self,
        surface: Surface,
        radius,
        explode_duration,
        tile_icon: tuple | Surface,
        explosion_color,
        key: str,
        nickname: str,
        price: int,
        sounds: list,
        create_button=True,
        buttonname="NONE",
    ) -> None:
        self.surface = surface
        self.key = key
        self.nickname = nickname
        self.radius = radius
        if isinstance(tile_icon, str):
            self.tile_icon = strToRGB(tile_icon)
        else:
            self.tile_icon = tile_icon
        self.tiles = set()
        self.explode_duration = explode_duration
        self.explosion_color = explosion_color
        self.price = price
        self.sounds = sounds
        if create_button:
            BombButton(surface, buttonname, 0, 0, 0, 0, self.nickname, self)

        Bomb.explode_durations.append(self.explode_duration)

    def setSurface(self, surface):
        """Updated the self.surface variable of the bomb"""
        self.surface = surface

    @abc.abstractmethod
    def draw(self):
        """
        This abstract method is for implementing the drawing of
        every tile on wich a bomb is placed.
        """

    @abc.abstractmethod
    def calculateAreas(self):
        """
        This abstract method is for implementing the calculation of
        where a bomb explodes.
        """

    @abc.abstractmethod
    def explode(self):
        """
        This abstract method is for implementing the functionality
        that will be called when the bomb explodes. Including
        drawing the previously calculated areas.
        """


class ConventionalBomb(Bomb):
    """
    A conventional bomb simply explodes in a square.
    The size of the square is defined by the radius."""

    def __init__(
        self,
        screen,
        radius,
        explode_duration,
        tile_icon: tuple | Surface,
        key: str,
        nickname: str,
        price: int,
    ) -> None:
        super().__init__(
            screen,
            radius,
            explode_duration,
            tile_icon,
            shared.COLORS["game"]["bombs"]["conventional"]["explosion-area"],
            key,
            nickname,
            price,
            [
                join("..", "assets", "sounds", "explosion01.mp3"),
                join("..", "assets", "sounds", "explosion02.mp3"),
            ],
            create_button=True,
            buttonname=key,
        )
        self.explosion_area: set[tuple[int, int]] = set()

    def draw(self):
        if isinstance(self.tile_icon, tuple):
            for loc in self.tiles:
                real_loc = cordsConvert(loc, shared.tile_size, True)
                rect = Rect(
                    real_loc[0], real_loc[1], shared.tile_size, shared.tile_size
                )
                draw.rect(self.surface, self.tile_icon, rect)
        elif isinstance(self.tile_icon, Surface):
            for loc in self.tiles:
                real_loc = cordsConvert(loc, shared.tile_size, True)
                tile_icon_scaled = transform.scale(
                    self.tile_icon, (shared.tile_size, shared.tile_size)
                )
                self.surface.blit(tile_icon_scaled, (real_loc[0], real_loc[1]))
        else:
            raise TypeError(f"Invalid type '{type(self.tile_icon)}' for self.tile_icon")

    def calculateAreas(self):
        """This bomb type has only 1 area: explosion_area"""
        self.explosion_area.clear()
        for loc in self.tiles:
            rect = [
                loc[0] - self.radius,  # top_left_x
                loc[1] - self.radius,  # top_left_y
                loc[0] + self.radius,  # bottom_right_x
                loc[1] + self.radius,  # bottom_right_y
            ]  # not a pygame rect!
            for x in range(rect[0], rect[2] + 1):
                for y in range(rect[1], rect[3] + 1):
                    self.explosion_area.add((x, y))

    def explode(self, current_t, explode_t):
        if not current_t - self.explode_duration <= explode_t or self.tiles == set():
            return
        for explosion_effect in self.explosion_area:
            real_loc = cordsConvert(explosion_effect, shared.tile_size, True)
            draw.rect(
                self.surface,
                self.explosion_color,
                Rect(real_loc[0], real_loc[1], shared.tile_size, shared.tile_size),
            )


class ClusterBomb(Bomb):
    """
    A cluster bomb explodes on a random amount of tiles within a square.
    The size of the square is determined by the radius
    and the amount of epxlosions is roughly controlled
    by the treshhold (given in %).
    """

    def __init__(
        self,
        surface: Surface,
        radius: int,
        threshold: int,
        explode_duration,
        tile_icon: tuple | Surface,
        key: str,
        nickname: str,
        price: int,
    ) -> None:
        super().__init__(
            surface,
            radius,
            explode_duration,
            tile_icon,
            shared.COLORS["game"]["bombs"]["cluster"]["explosion-area"],
            key,
            nickname,
            price,
            [join("..", "assets", "sounds", "explosion02.mp3")],
            buttonname=key,
        )
        self.threshold = threshold
        self.explosion_area: set[tuple[int, int]] = set()

    def draw(self):
        return ConventionalBomb.draw(self)

    def calculateAreas(self):
        """This bomb has only 1 area: explosion_area,
        but unlike a conventional bomb only some tiles in the radius will explode."""
        self.explosion_area.clear()
        for loc in self.tiles:
            rect = [
                loc[0] - self.radius,  # top_left_x
                loc[1] - self.radius,  # top_left_y
                loc[0] + self.radius,  # bottom_right_x
                loc[1] + self.radius,  # bottom_right_y
            ]  # not a pygame rect!
            for x in range(rect[0], rect[2] + 1):
                for y in range(rect[1], rect[3] + 1):
                    if randint(0, 100) > self.threshold:
                        self.explosion_area.add((x, y))

    def explode(self, current_t, explode_t):
        return ConventionalBomb.explode(self, current_t, explode_t)
