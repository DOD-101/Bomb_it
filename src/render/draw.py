"""
Implements the draw class, which contains all draw functions.

Status: Working
"""
import time
import os
import re
from json import load
from math import ceil

from pygame import Surface, Rect, draw, image, transform
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
        self.score_page = 0

    def updateSurface(self, surface):
        self.surface = surface

    def drawDashedLine(self, start_x, end_x, y, line_width, dash_length, gap_length, color):
        # Draw a dashed line
        x = start_x + dash_length
        last_x = start_x
        while x < end_x:
            draw.line(self.surface, color, (last_x,y), (x, y), line_width)
            last_x = x + gap_length
            x += dash_length + gap_length

    def drawGrid(self):
        '''Used to draw base grid before effects'''
        self.surface.fill(shared.COLORS["all"]["background"])

        pix_x, pix_y = 0,0
        pxmap = shared.immap.load()
        for x in range(shared.grid_start, shared.immap.size[0]*shared.tile_size + shared.grid_start, shared.tile_size):
            for y in range(0, shared.immap.size[1]*shared.tile_size, shared.tile_size):
                rect = Rect(x, y, shared.tile_size, shared.tile_size)
                pydraw.rect(self.surface, pxmap[pix_x,pix_y], rect)
                pydraw.rect(self.surface, shared.COLORS["game"]["grid-border"], rect, 1)
                pix_y += 1
            pix_x += 1
            pix_y = 0

    def drawTileIcons(self):
        TILE_ICON_LOC = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'assets', 'tile_icons')
        icon_num = 0
        def tileBliting(position):
            tile_icon_path = os.path.join(TILE_ICON_LOC, tile_icons[position]) + '.png'
            tile_surface = image.load(tile_icon_path).convert()
            tile_surface = transform.scale(tile_surface,[shared.tile_size, shared.tile_size])
            self.surface.blit(tile_surface, real_cord)

        for color in shared.mapcolors: # get the color
            for tile in shared.TILES.values(): # get every tile
                if tuple(tile["color"]) == color: # check if it's the right tile
                    if tile["icons"] != ["NONE"]: # check if the tile has (an) icon(s)
                        for cord in shared.mapcolors[color]:
                            #convert the cord to real cord
                            real_cord = cordsConvert(cord, shared.tile_size, to_normal=True)
                            #place proper blit
                            tile_icons = tile["icons"]

                            if len(tile_icons) == 1:
                                tileBliting(0)
                            else:
                                if icon_num == len(tile_icons):
                                    icon_num = 0
                                tileBliting(icon_num)
                                icon_num += 1
                    else:
                        break

    def drawMenu(self, explode_time, total_score):
        """Draws anything outside of the grid"""
        draw.rect(self.surface, shared.COLORS["all"]["background"], Rect(0, 0, shared.grid_start, shared.window_h))
        draw.rect(self.surface, shared.COLORS["all"]["background"], Rect(shared.grid_start, shared.grid_bottom, shared.window_w, shared.window_h))
        RoundButton(self.surface, "back", shared.COLORS["all"]["back_btn"]["stage1"], 10, 10, 30, 30, "<", shared.STANDARD_FONT, shared.COLORS["all"]["back_btn"]["font1"], [shared.COLORS["all"]["back_btn"]["border1"], "3"], insta_draw=True)

        #region BombButton drawing
        bomb_button_y_pos = 50
        for bomb_button in BombButton.instances.values():
            bomb_button.x_pos = 20
            bomb_button.y_pos = bomb_button_y_pos
            bomb_button.width = 100
            bomb_button.height = 50

            bomb_button.setSurface(shared.screen)
            bomb_button.draw()
            bomb_button_y_pos += 60

        Button(self.surface, "clear", shared.COLORS["game"]["clear_btn"]["stage1"], 10, shared.window_h - 210, 150, 50, "Clear bombs", shared.STANDARD_FONT, shared.COLORS["game"]["clear_btn"]["font1"], [shared.COLORS["game"]["clear_btn"]["border1"], 3, 4], insta_draw=True)
        Button(self.surface, "nextmap", shared.COLORS["game"]["next_map_btn"]["stage1"], 10, shared.window_h - 150, 150, 50, "Next map", shared.STANDARD_FONT, shared.COLORS["game"]["next_map_btn"]["font1"], [shared.COLORS["game"]["next_map_btn"]["border1"] ,3, 4], insta_draw=True)
        #endregion
        if time.time() >= explode_time + max(Bomb.explode_durations):
            Button(self.surface, "explode", shared.COLORS["game"]["explode_btn"]["stage1"], 10, shared.window_h - 90, 150, 50, "EXPLODE!", shared.STANDARD_FONT, shared.COLORS["game"]["explode_btn"]["font1"],[shared.COLORS["game"]["explode_btn"]["border1"] ,3, 4], insta_draw=True)
        else:
            Button(self.surface, "explode", shared.COLORS["game"]["explode_btn"]["stage2"], 10, shared.window_h - 90, 150, 50, "EXPLODE!", shared.STANDARD_FONT, shared.COLORS["game"]["explode_btn"]["font2"], [shared.COLORS["game"]["explode_btn"]["border2"] ,3, 4], insta_draw=True)


        # draw active-bomb text
        active_bomb_font = shared.STANDARD_FONT
        active_bomb_font_color = shared.COLORS["game"]["active_bomb-font"]
        active_bomb_ftext = active_bomb_font.render(shared.active_bomb.nickname, True, active_bomb_font_color)
        draw.rect(self.surface, shared.COLORS["all"]["background"], [0, shared.window_h-30, 190, 30])
        self.surface.blit(active_bomb_ftext, (20, shared.window_h - 40))
        # draw score text
        total_score_font = active_bomb_font
        part_score_font = Font(os.path.join('..', 'assets',  'fonts', 'OpenSans', 'static', 'OpenSans_Condensed-SemiBold.ttf'), 20)
        part_score_font_color = shared.COLORS["game"]["part_score-font"]
        part_score_y = shared.window_h - 270 - (len(shared.score_parts) * 30)
        for key, value in shared.score_parts.items():
            part_score_ftext = part_score_font.render(f"{key}: {value}", True, part_score_font_color)
            self.surface.blit(part_score_ftext, (20, part_score_y))
            part_score_y += 30

        self.drawDashedLine(20, 150, shared.window_h - 262, 2, 10, 7, shared.COLORS["game"]["score_line"])

        total_score_font_color = shared.COLORS["game"]["total_score-font"]
        total_score_ftext = total_score_font.render(f"Score:{total_score}", True, total_score_font_color)
        self.surface.blit(total_score_ftext, (20, shared.window_h - 260))

        Button(self.surface, "score", shared.COLORS["game"]["score_btn"]["stage1"], 170 ,shared.window_h - 210, 20, 20, "", shared.STANDARD_FONT, (0,0,0), border=[shared.COLORS["game"]["score_btn"]["border1"], 3, 4] ,insta_draw = True)

        score_icon = image.load(os.path.join("..", "assets", "icons", "score_list.png")).convert()
        score_icon = transform.scale(score_icon, [19, 19])
        shared.screen.blit(score_icon, [170, shared.window_h - 210])

    def drawScoreScreen(self):
        backdrop_box_width, box_height = shared.window_w / 2.5, shared.window_h / 1.2
        main_backdrop_cords = center(backdrop_box_width, box_height, shared.window_w, shared.window_h, "both")
        backdrop_box = (main_backdrop_cords[0], main_backdrop_cords[1], backdrop_box_width, box_height)
        main_backdrop = Rect(backdrop_box)

        pydraw.rect(self.surface, shared.COLORS["score"]["window_background"], main_backdrop, border_radius= 10)

        pydraw.line(self.surface, shared.COLORS["score"]["top_line"], (backdrop_box[0], backdrop_box[1] + 70), \
                    (backdrop_box[0]+ backdrop_box_width, backdrop_box[1] + 70), 2)

        mapname = shared.map_queue[0].rpartition('_')[0]

        # loads in scores.json
        with open(os.path.join('..', 'userdata', 'scores.json'), 'r') as json_file:
            MAP_SCORES = load(json_file)

        # gets the highest score
        if mapname in MAP_SCORES:
            # all_map_scores contains all sore data (score, time, bomb-location) for every time there was a score
            # equivalent to the 0, 1, 2... entries in scores.json
            all_map_scores = [score for score in MAP_SCORES[mapname].values()]
            all_map_scores.reverse()
            highest_score = max([score[0] for score in MAP_SCORES[mapname].values()])
        else:
            highest_score = 0
            all_map_scores = []

        # blits header containing map name and high score
        header_font = shared.STANDARD_FONT
        header_color = shared.COLORS["score"]["header_font"]

        header_ftext = header_font.render(f"{mapname} high score: {highest_score}", True, header_color)
        self.surface.blit(header_ftext, (backdrop_box[0] + 5, backdrop_box[1] + 10))

        # region Blting items aka. score instances

        item_font = shared.STANDARD_FONT
        item_color = shared.COLORS["score"]["item_font"]

        item_y = backdrop_box[1] + 75
        items_per_page = int((box_height - 75 - 50) / 30) if not 0 else 1 # 75: top header; 50: bottom button bar; 30: height of every item
        items_per_page = items_per_page if items_per_page != 0 else 1
        pages_needed = ceil(len(all_map_scores) / items_per_page)
        place_icon = image.load(os.path.join("..", "assets", "icons", "place.png")).convert_alpha()
        # place_icon = transform.smoothscale(place_icon, [16,16])
        # gets all scores to be displayed on page and displays them
        for score_time in all_map_scores[self.score_page * items_per_page : self.score_page * items_per_page + items_per_page]:
            item_ftext = item_font.render(f"{score_time[0]} : {score_time[1]}", True, item_color)
            self.surface.blit(item_ftext, (backdrop_box[0] + 5, item_y))

            place_button_rect = [backdrop_box[0] + backdrop_box[2] - 40, item_y + 5, 25, 25]
            Button(self.surface, f"bomb_place_{len(all_map_scores) - all_map_scores.index(score_time) - 1}", shared.COLORS["score"]["window_background"], \
                     place_button_rect[0], place_button_rect[1], place_button_rect[2], place_button_rect[3],"", shared.STANDARD_FONT, "white", insta_draw=True)
            shared.screen.blit(place_icon, place_button_rect)
            item_y += 30

        # endregion

        # Blting of page buttons at the bottom of the window
        x = backdrop_box[0] + (backdrop_box_width - 40 * pages_needed) / 2
        button_y = backdrop_box[1] + box_height - 40
        for p in range(pages_needed):
            RoundButton(self.surface, f"page_btn_{p}", shared.COLORS["score"]["page_btn"]["stage1"], x, button_y, 30, 30, str(p + 1), shared.STANDARD_FONT, shared.COLORS["score"]["page_btn"]["font1"], [shared.COLORS["score"]["page_btn"]["border1"], 2], insta_draw=True)

            x += 40

    def drawEfects(self, mouse_pos, mouse_tile_cords, explode_t):
        #clicked efects
        for bomb in Bomb.instances.values():
            bomb.setSurface(shared.screen)
            bomb.draw()
        #hover efect
        if mouse_pos[0] > shared.grid_start and mouse_pos[1] < shared.immap.size[1] * shared.tile_size:
            hover_Surface = Surface((shared.tile_size, shared.tile_size))
            hover_Surface.set_alpha(128)
            hover_Surface.fill(shared.COLORS["game"]["grid-hover"])
            blit_x, blit_y = cordsConvert(mouse_tile_cords, shared.tile_size, True)
            self.surface.blit(hover_Surface,(blit_x, blit_y))
        #explosions of bombs
        current_time = time.time()
        for bomb in Bomb.instances.values():
            bomb.explode(current_time, explode_t)
        # bomb explosion radius on hover
        for bomb in Bomb.instances.values():
            bomb.radius
            for tile in bomb.tiles:
                position = cordsConvert(tile, shared.tile_size, True)
                if mouse_pos[0] > position[0] and mouse_pos[1] > position[1] and \
                    mouse_pos[0] < position[0] + shared.tile_size and mouse_pos[1] < position[1] + shared.tile_size:
                    size = bomb.radius * shared.tile_size * 2 + shared.tile_size
                    position = list(map(lambda x: x + shared.tile_size/2, position))
                    self._draw_centered_dashed_rect(self.surface, "red", position, [size, size], 10, 5)

    def drawStartMenu(self):
        self.surface.fill(shared.COLORS["all"]["background"])
        menu_btn_font = Font(os.path.join('..', 'assets', 'fonts', 'OpenSans', 'static', 'OpenSans-ExtraBold.ttf'), 38)
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
        RoundButton(self.surface, "mapback", shared.COLORS["all"]["back_btn"]["stage1"], 20, 20, 30, 30, "<", shared.STANDARD_FONT,shared.COLORS["all"]["back_btn"]["font1"],[shared.COLORS["all"]["back_btn"]["border1"], "3"], insta_draw = True)

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

    def _draw_dashed_line(self, surface, color, start_pos, end_pos, dash_length, width):
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = x2 - x1
        dy = y2 - y1
        distance = max(abs(dx), abs(dy))
        for i in range(0, distance, 2 * dash_length):
            start = (x1 + dx * i / distance, y1 + dy * i / distance)
            end = (x1 + dx * (i + dash_length) / distance, y1 + dy * (i + dash_length) / distance)
            draw.line(surface, color, start, end, width)

    def _draw_dashed_rect(self, surface, color, rect, dash_length, width):
        x, y, w, h = rect
        self._draw_dashed_line(surface, color, (x, y), (x+w, y), dash_length, width)  # Top border
        self._draw_dashed_line(surface, color, (x, y), (x, y+h), dash_length, width)  # Left border
        self._draw_dashed_line(surface, color, (x+w, y), (x+w, y+h), dash_length, width)  # Right border
        self._draw_dashed_line(surface, color, (x, y+h), (x+w, y+h), dash_length, width)  # Bottom border

    def _draw_centered_dashed_rect(self, surface, color, center, size, dash_length, width):
        x, y = center
        w, h = size
        rect = Rect(0, 0, w, h)
        rect.center = (x, y)
        self._draw_dashed_rect(surface, color, rect, dash_length, width)