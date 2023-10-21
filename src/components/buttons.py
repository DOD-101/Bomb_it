"""
Implements all Button Classes.

Status: WIP
- Bomb is needed for type hinting. Fix this issue once the Bomb class has it's own file"
"""

from typing import Literal

from pygame import draw as pydraw
from pygame import Surface

import shared
from src.utils.utils import strToRGB, center
from bombs import Bomb

class Button:
    instances = {}
    def __init__(self, surface: Surface, color ,x_pos: int, y_pos: int, width:int, height: int, text: str, font, font_color, border: Literal["color","width","radius"] = None, insta_draw: bool = False) -> None:
        self.surface = surface
        self.color = strToRGB(color)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.font_Color = strToRGB(font_color)
        self.ftext = self.font.render(text, True, font_color)
        if not border == None:
            self.border = border
            self.border[0] = strToRGB(self.border[0])
            self.border[1] = int(self.border[1])
            self.border[2] = int(self.border[2])

        if insta_draw == True:
            self.draw()

    def draw(self) -> None:
        pydraw.rect(self.surface, self.color, [self.x_pos, self.y_pos, self.width,self.height])
        if hasattr(self, "border"):
            pydraw.rect(self.surface, self.border[0], [self.x_pos - (self.border[1] / 2), self.y_pos - (self.border[1] / 2), self.width + self.border[1],self.height + self.border[1]], self.border[1], self.border[2])
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
    def __init__(self, color, x_pos: int, y_pos: int, width: int, height: int, text: str, font, font_color, border: Literal['color', 'width'] = None, insta_draw: bool = False) -> None:
        super().__init__(color, x_pos, y_pos, width, height, text, font, font_color, [*border, 0], insta_draw)

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
        self.text_centered_y = self.y_pos + center(item_height = self.text_height, parent_height = self.height, center_direction = 'vertical')
        self.surface.blit(self.ftext, (self.text_centered_x, self.text_centered_y))

    def checkmouseover(self, mouse_pos) -> bool:
        dx = mouse_pos[0] - self.cpt_x
        dy = (mouse_pos[1] - self.cpt_y) * self.scale_y
        collide =  dx*dx + dy*dy <= self.semi_axis_a*self.semi_axis_a
        if collide:
            print("Yes", end="")
            return True
        else:
            return False

class BombButton(Button):
    '''Use this class to make any BombButtons so that they all have certain atributes the same'''
    instances = {}
    def __init__(self, x_pos: int, y_pos: int, width: int, height: int, text: str, bombinstance: type[Bomb], insta_draw = False) -> None:
        super().__init__(shared.colors["game"]["bomb-buttons"]["conventional"]["stage1"], x_pos, y_pos, width, height, text, shared.STANDARD_FONT, shared.colors["game"]["bomb-buttons"]["conventional"]["font1"], insta_draw = insta_draw)
        self.bombinstance = bombinstance

    def onclick(self):
        global active_bomb_text, active_bomb
        active_bomb_text = self.bombinstance.nickname
        active_bomb = Bomb.instances[self.bombinstance.key]

    def checkAndExecute(self, mouse_pos):
        if super().checkmouseover(mouse_pos):
            self.onclick()
