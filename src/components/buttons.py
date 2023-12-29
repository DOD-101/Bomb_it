"""
Implements all Button Classes.

Status: Working
"""

from typing import Literal

from pygame import draw as pydraw
from pygame import Surface, transform

import shared
from utils.utils import strToRGB, center

class Button:
    instances = {}
    def __init__(self, surface: Surface, name: str, color ,x_pos: int, y_pos: int, width:int, height: int, text: str, font, font_color, border: Literal["color","width","radius"] = None, insta_draw: bool = False) -> None:
        self.surface = surface
        Button.instances[name] = self
        self.color = strToRGB(color)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.font_color = strToRGB(font_color)
        self.ftext = self.font.render(text, True, font_color)
        if not border == None:
            self.border = border
            self.border[0] = strToRGB(self.border[0])
            self.border[1] = int(self.border[1])
            self.border[2] = int(self.border[2])
        if insta_draw == True:
            self.draw()

    def setSurface(self, surface):
        """Updated the self.surface variable of the button"""
        self.surface = surface

    def draw(self, draw_text=True) -> None:
        pydraw.rect(self.surface, self.color, [self.x_pos, self.y_pos, self.width,self.height])
        if hasattr(self, "border"):
            pydraw.rect(self.surface, self.border[0], [self.x_pos - (self.border[1] / 2), self.y_pos - (self.border[1] / 2), self.width + self.border[1],self.height + self.border[1]], self.border[1], self.border[2])
        if draw_text:
            self.text_width  = self.ftext.get_width()
            self.text_height = self.ftext.get_height()
            self.text_centered_x = self.x_pos + center(item_width = self.text_width, parent_width = self.width, center_direction = 'horizontal')
            self.text_centered_y = self.y_pos + center(item_height = self.text_height, parent_height = self.height, center_direction = 'vertical')
            self.surface.blit(self.ftext, (self.text_centered_x, self.text_centered_y))

    def checkmouseover(self, mouse_pos) -> bool:
        if self.x_pos <= mouse_pos[0] <= self.x_pos + self.width and self.y_pos <= mouse_pos[1] <= self.y_pos + self.height:
            return True
        else:
            return False

class RoundButton(Button):
    """Draws a button as an ellipse"""
    def __init__(self, surface: Surface, name: str, color, x_pos: int, y_pos: int, width: int, height: int, text: str, font, font_color, border: Literal['color', 'width'] = None, insta_draw: bool = False) -> None:
        super().__init__(surface, name, color, x_pos, y_pos, width, height, text, font, font_color, [*border, 0], insta_draw)

        # math from https://stackoverflow.com/questions/59971407/how-can-i-test-if-a-point-is-in-an-ellipse
        self.semi_axis_a = self.width // 2
        self.semi_axis_b = self.width // 2
        self.scale_y = self.semi_axis_a / self.semi_axis_b
        self.cpt_x, self.cpt_y = self.x_pos + self.width / 2, self.y_pos + self.height / 2

    def draw(self) -> None:
        pydraw.ellipse(self.surface, self.color, [self.x_pos, self.y_pos, self.width,self.height])
        if hasattr(self, "border"):
            pydraw.ellipse(self.surface, self.border[0], [self.x_pos - (self.border[1] / 2), self.y_pos - (self.border[1] / 2), self.width + self.border[1],self.height + self.border[1]], self.border[1])
        self.text_width  = self.ftext.get_width()
        self.text_height = self.ftext.get_height()
        self.text_centered_x = self.x_pos + center(item_width = self.text_width, parent_width = self.width, center_direction = 'horizontal')
        self.text_centered_y = self.y_pos + center(item_height = self.text_height, parent_height = self.height, center_direction = 'vertical') - 1 # to make text apear more centered
        self.surface.blit(self.ftext, (self.text_centered_x, self.text_centered_y))

    def checkmouseover(self, mouse_pos) -> bool:
        dx = mouse_pos[0] - self.cpt_x
        dy = (mouse_pos[1] - self.cpt_y) * self.scale_y
        collide =  dx*dx + dy*dy <= self.semi_axis_a*self.semi_axis_a
        if collide:
            return True
        else:
            return False

class BombButton(Button):
    '''Use this class to make any BombButtons so that they all have certain atributes the same'''
    instances = {}
    def __init__(self, surface: Surface, name: str, x_pos: int, y_pos: int, width: int, height: int, text: str, bombinstance: type["Bomb"],insta_draw = False) -> None: #type: ignore -- keeps complaining about type["Bomb"]
        super().__init__(surface, name, shared.COLORS["game"]["bomb-buttons"]["conventional"]["stage1"], x_pos, y_pos, width, height, text, shared.STANDARD_FONT, \
                         shared.COLORS["game"]["bomb-buttons"]["conventional"]["font1"], [shared.COLORS["all"]["background"], 6, 10],insta_draw = insta_draw)
        self.bombinstance = bombinstance
        BombButton.instances[name] = self

    def onclick(self):
        global active_bomb_text, active_bomb
        from .bombs import Bomb # put here to avoid circular import
        shared.active_bomb_text = self.bombinstance.nickname
        shared.active_bomb = Bomb.instances[self.bombinstance.key]

    def draw(self):
        super().draw(draw_text=False)

        fdivider = self.font.render("|", True, self.font_color)
        fdivider_cords = [self.width / 2 + self.x_pos, self.y_pos]
        self.surface.blit(fdivider, fdivider_cords)
        # bliting text

        scale_factor = fdivider_cords[0] / (self.x_pos + 10 + self.ftext.get_width())
        if scale_factor < 1:
            self.ftext = transform.smoothscale_by(self.ftext, scale_factor)

        self.text_width  = self.ftext.get_width()
        self.text_height = self.ftext.get_height()
        self.text_centered_y = self.y_pos + center(item_height = self.text_height, parent_height = self.height, center_direction = 'vertical')
        self.text_cords = [self.x_pos + 10, self.text_centered_y]

        self.surface.blit(self.ftext, self.text_cords)

        self.fprice = self.font.render(str(self.bombinstance.price), True, self.font_color)
        self.fprice_height = self.fprice.get_height()
        self.fprice_centered_y = self.y_pos + center(item_height = self.fprice_height, parent_height = self.height, center_direction = 'vertical')
        self.surface.blit(self.fprice, [fdivider_cords[0] + 20, self.fprice_centered_y])

    def checkAndExecute(self, mouse_pos):
        if super().checkmouseover(mouse_pos):
            self.onclick()
