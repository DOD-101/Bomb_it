"""
Implements the draw class, which contains all draw functions.

Status: Working
"""
import time
import os
import re

from pygame import Surface, Rect, draw
from pygame import draw as pydraw
from pygame.font import Font

import shared

from components.buttons import Button, BombButton, RoundButton
from components.mapframe import MapFrame
from components.bombs import Bomb
from utils.utils import cordsConvert, center


class Draw:
    def __init__(self, surface: Surface) -> None:
        self.surface = surface

    def updateSurface(self, surface):
        self.surface = surface

    def drawGrid(self, map_image, grid_start: int):
        '''Used to draw base grid before effects'''
        self.surface.fill(shared.COLORS["all"]["background"])

        pix_x, pix_y = 0,0
        pxmap = map_image.load()
        for x in range(grid_start, map_image.size[0]*shared.tile_size + grid_start, shared.tile_size):
            for y in range(0, map_image.size[1]*shared.tile_size, shared.tile_size):
                rect = Rect(x, y, shared.tile_size, shared.tile_size)
                pydraw.rect(self.surface, pxmap[pix_x,pix_y], rect)
                pydraw.rect(self.surface, shared.COLORS["game"]["grid-border"], rect, 1)
                pix_y += 1
            pix_x += 1
            pix_y = 0

    def drawMenu(self, explode_time, total_score):
        draw.rect(self.surface,shared.COLORS["all"]["background"], Rect(0, 0, shared.MENU_WIDTH, shared.window_h))
        #region BombButton drawing
        bomb_button_y_pos = 30
        for bomb_button in BombButton.instances.values():
            bomb_button.x_pos = 20
            bomb_button.y_pos = bomb_button_y_pos
            bomb_button.width = 100
            bomb_button.height = 50

            bomb_button.setSurface(shared.screen)
            bomb_button.draw()
            bomb_button_y_pos += 60

        #endregion
        if time.time() >= explode_time + max(Bomb.explode_durations):
            Button(self.surface, "explode", shared.COLORS["game"]["explode_btn"]["stage1"], 10, shared.window_h - 90, 150, 50, "EXPLODE!", shared.STANDARD_FONT,shared.COLORS["game"]["explode_btn"]["font1"],[shared.COLORS["game"]["explode_btn"]["border1"] ,3, 4], insta_draw=True)
        else:
            Button(self.surface, "explode", shared.COLORS["game"]["explode_btn"]["stage2"], 10, shared.window_h - 90, 150, 50, "EXPLODE!", shared.STANDARD_FONT,shared.COLORS["game"]["explode_btn"]["font2"],[shared.COLORS["game"]["explode_btn"]["border2"] ,3, 4], insta_draw=True)

        Button(self.surface, "nextmap", shared.COLORS["game"]["next_map_btn"]["stage1"], 10, shared.window_h - 150, 150, 50, "Next map", shared.STANDARD_FONT,shared.COLORS["game"]["next_map_btn"]["font1"],[shared.COLORS["game"]["next_map_btn"]["border1"] ,3, 4], insta_draw=True)

        # draw active-bomb text
        active_bomb_font = shared.STANDARD_FONT
        active_bomb_font_color = shared.COLORS["game"]["active_bomb-font"]
        active_bomb_ftext = active_bomb_font.render(shared.active_bomb.nickname, True, active_bomb_font_color)
        draw.rect(self.surface, shared.COLORS["all"]["background"], [0, shared.window_h-30, 190, 30])
        self.surface.blit(active_bomb_ftext, (20, shared.window_h - 40))
        # draw score text
        total_score_font = active_bomb_font
        total_score_font_color = shared.COLORS["game"]["total_score-font"]
        total_score_ftext = total_score_font.render(f"Score:{total_score}", True, total_score_font_color)
        self.surface.blit(total_score_ftext, (20, shared.window_h - 200))

    def drawEfects(self, mouse_pos, mouse_tile_cords, explode_t):
        #hover efect
        if mouse_pos[0] > shared.grid_start and mouse_pos[1] < shared.immap.size[1] * shared.tile_size:
            hover_Surface = Surface((shared.tile_size, shared.tile_size))
            hover_Surface.set_alpha(128)
            hover_Surface.fill(shared.COLORS["game"]["grid-hover"])
            blit_x, blit_y = cordsConvert(mouse_tile_cords, shared.tile_size, True)
            self.surface.blit(hover_Surface,(blit_x, blit_y))
        #clicked efects
        for bomb in Bomb.instances.values():
            bomb.setSurface(shared.screen)
            bomb.draw()
        #explosions of bombs
        current_time = time.time()
        for bomb in Bomb.instances.values():
            bomb.explode(current_time, explode_t)

    def drawStartMenu(self):
        self.surface.fill(shared.COLORS["all"]["background"])
        menu_btn_font = Font('..\\assets\\fonts\OpenSans\static\OpenSans-ExtraBold.ttf', 38)
        menu_btn_color = shared.COLORS["start_menu"]["button-background"]
        launch_btn_size = (300, 50)
        launch_btn_location = center(launch_btn_size[0], launch_btn_size[1], shared.window_w, shared.window_h, "both")
        Button(self.surface, "launch", menu_btn_color, launch_btn_location[0], launch_btn_location[1], launch_btn_size[0], launch_btn_size[1], "Launch!", menu_btn_font, shared.COLORS["start_menu"]["button-font"], insta_draw=True)

        mapselect_btn_size = launch_btn_size
        mapselect_btn_location = (launch_btn_location[0], launch_btn_location[1] + 80)
        Button(self.surface, "mapselect", menu_btn_color, mapselect_btn_location[0], mapselect_btn_location[1], mapselect_btn_size[0], mapselect_btn_size[1], "Map selection", menu_btn_font, shared.COLORS["start_menu"]["button-font"], insta_draw=True)

    def drawMapSelect(self):
        self.surface.fill(shared.COLORS["all"]["background"])
        MapFrame.instance_num = 0
        MapFrame.row = 0
        RoundButton(self.surface, "mapback", shared.COLORS["all"]["back_button"]["stage1"], 20, 20, 30, 30, "<", shared.STANDARD_FONT,shared.COLORS["all"]["back_button"]["font1"],[shared.COLORS["all"]["back_button"]["border1"], "3"], insta_draw = True)

        for map in os.listdir(shared.PATH_TO_MAPS):
            file_ending = re.search(r".*(\..*)$", map).group(1)
            if file_ending != ".png":
                continue
            MapFrame(self.surface, shared.COLORS["map_select"]["map-frame"], os.path.join(shared.PATH_TO_MAPS, map), map.removesuffix(file_ending))

        #region Map queue
        self.map_queue_x_buttons_dict = {} # should be moved to it's own x_button class in the future
        map_queue_element_height = 50
        def draw_map_queue_element(top_y: int, mapname: str):
            draw.rect(self.surface, shared.COLORS["map_select"]["queue"]["element"]["border"], [5, top_y, shared.MAP_QUEUE_W - 10, map_queue_element_height], 1)
            mapname_text_font = shared.STANDARD_FONT
            mapname_text = mapname.rpartition('_')[0]
            mapname_ftext = mapname_text_font.render(mapname_text, True, shared.COLORS["map_select"]["queue"]["element"]["text"])
            mapname_width, mapname_height = mapname_ftext.get_size()
            mapname_y = top_y + center(item_height = mapname_height, parent_height = 50, center_direction = "vertical")
            self.surface.blit(mapname_ftext, [10, mapname_y])

            # X button
            x_text_font = shared.STANDARD_FONT
            x_ftext = x_text_font.render("x", True, (0,0,0)) #color does not matter
            x_ftext_width, x_ftext_height = x_ftext.get_size()
            x_ftext_y =  top_y + center(item_height = x_ftext_height, parent_height = 50, center_direction = "vertical")
            self.map_queue_x_buttons_dict[mapname] = Button(self.surface, mapname, shared.COLORS["all"]["background"], shared.MAP_QUEUE_W - 15 - x_ftext_width, x_ftext_y, x_ftext_width, x_ftext_height, "x", x_text_font,  shared.COLORS["map_select"]["queue"]["element"]["x-button"], insta_draw = True)

        draw.line(self.surface, shared.COLORS["map_select"]["queue"]["line"], [shared.MAP_QUEUE_W, 0], [shared.MAP_QUEUE_W, shared.window_h], 2)

        top_y = 100
        for map in shared.map_queue:
            draw_map_queue_element(top_y, map)
            top_y += map_queue_element_height + 5
        #endregion

        map_launch_btn_size = (190, 50)
        map_launch_btn_x, map_launch_btn_y = center(item_width = map_launch_btn_size[0], parent_width = shared.MAP_QUEUE_W, center_direction="horizontal"), shared.window_h - map_launch_btn_size[1] - 5
        Button(self.surface, "maplaunch", shared.COLORS["map_select"]["launch_btn"]["stage1"], map_launch_btn_x, map_launch_btn_y, map_launch_btn_size[0], map_launch_btn_size[1], "Launch!", shared.STANDARD_FONT,shared.COLORS["map_select"]["launch_btn"]["font1"], insta_draw=True)
