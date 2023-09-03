import pygame
import pygame_widgets as pyw

import abc
import time
import os
import typing
import re
import uuid
import random
import json

from PIL import Image
from utils import utils
from utils import map_utils
center = utils.center
strtoRGB = utils.strToRGB


window_w = 1000
window_h = 300
score_functions = set()

def main():
    global screen, mouse_pos, active_bomb_text, active_bomb, selection, kt10, kt50, kt100, explode_time, \
          window_w, window_h, grid_start, grid_bottom, map_row_lengh, map_queue, map_queue_x_buttons_dict, standard_font, immap, total_score, mapcolors, \
          colors
    pygame.init()
    pygame.display.set_caption("Bomb It!")
    standard_font = pygame.font.SysFont('Bahnschrift SemiBold', 30)

    map_row_lengh = int((window_w - map_queue_w) / 280)
    if map_row_lengh == 0:
        map_row_lengh = 1
    screen = pygame.Surface((1000, 1000))
    rscreen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)
    # Bombs
    kt10_img = pygame.image.load(os.path.join(SELF_LOC, "resources\\bomb_icons\\conventional\\test.png")).convert()
    Bomb.instances["kt10"] = ConventionalBomb(0, 3,kt10_img, "kt10", "G-kt10")
    Bomb.instances["kt50"] = ConventionalBomb(2, 3,(255, 102, 255), "kt50", "G-kt50")
    Bomb.instances["kt100"] = ConventionalBomb(5, 3,(102, 255, 102), "kt100", "G-kt100")

    #-----
    active_bomb_text = Bomb.instances["kt10"].nickname
    active_bomb = Bomb.instances["kt10"]

    map_queue = []

    total_score = 100

    running = "start"


    selecting = False
    game_clock = pygame.time.Clock()
    first_draw = True
    while not running == "quit":
        mouse_pos = pygame.mouse.get_pos()
        if running == "start":
            drawStartMenu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = "quit"
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if launch_btn.checkmouseover():
                        running = "game"
                        
                    
                    if mapselect_btn.checkmouseover():
                        running = "map_select"

                if event.type == pygame.VIDEORESIZE:
                    onWindowScale(event)

                    continue

            rscreen.blit(screen, (0,0))
            pygame.display.flip()

        if running == "map_select":


            drawMapSelect()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = "quit"
                    break
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if map_launch_btn.checkmouseover():
                        running = "game"
                        break

                    for map in mapdict.keys():
                        mapdict[map].checkANDExecute()

                    for x_button in map_queue_x_buttons_dict.keys():
                        if map_queue_x_buttons_dict[x_button].checkmouseover():
                            map_queue.remove(x_button)

                    if back_button.checkmouseover():
                        running = "start"
                    
                if event.type == pygame.VIDEORESIZE:
                    onWindowScale(event)

                    continue
            
            rscreen.blit(screen, (0,0))
            pygame.display.flip()


        if running == "game":
            if not len(map_queue) == 0:
                file_name = map_queue[0].rpartition('_')[0] + ".png"
            elif first_draw:
                possible_maps = []
                for map in  os.listdir("resources\maps"):
                    file_ending = re.search(r".*(\..*)$", map).group(1)
                    if not file_ending == ".png":
                        continue
                    possible_maps.append(map)
                file_name = possible_maps[random.randint(0, len(possible_maps) - 1)]

                    
            immap = Image.open(os.path.join(SELF_LOC, "resources\maps", file_name))
            mapcolors = map_utils.px_to_colordict(immap, [(0, 255, 0),(0, 0, 255),(255, 0, 255),(255, 0, 0),(0,0,0),(255, 255, 0)])
            getTileSize()
            grid_start = window_w - immap.size[0] * tile_size
            grid_bottom = immap.size[1] * tile_size
            mouseTilecords()
            drawGrid()
            drawEfects()
            drawMenu()
            first_draw = False
            # event handling, gets all events from the event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = "quit"
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for bomb_button in BombButton.instances.values():
                        bomb_button.checkAndExecute()

                    if explode_btn.checkmouseover() and time.time() >= explode_time + max(Bomb.explode_durations):
                        for bomb in Bomb.instances.values():
                            bomb.calculateAreas()
                        total_score = calculateTotalScore()
                        explode_time = time.time()
                    
                    if next_map_btn.checkmouseover():
                        if not len(map_queue) == 0:
                            del map_queue[0]
                        else:
                            first_draw = True

                    if mouse_pos[0] > MENU_WIDTH and selecting == False:
                        selecting = True
                        selection = list()
                        selection.append((tile_cord_x, tile_cord_y))

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and selecting == True:
                    selecting = False
                    selection.append((tile_cord_x, tile_cord_y))
                    if time.time() >= explode_time + max(Bomb.explode_durations):
                        selectTiles()

                if event.type == pygame.VIDEORESIZE:
                    onWindowScale(event)
                    getTileSize()
                    continue

            rscreen.blit(screen, (0,0))
            pygame.display.flip()

            game_clock.tick(FPS)

def onWindowScale(event):
    global screen, rscreen, window_w, window_h, map_row_lengh
    window_w, window_h = event.size
    map_row_lengh = int((window_w - map_queue_w) / 280)
    if map_row_lengh == 0:
        map_row_lengh = 1
    rscreen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)
    screen = pygame.transform.scale(screen, (window_w, window_h))
    screen.fill(colors["all"]["background"])

def getTileSize():
    global tile_size
    if window_w - MENU_WIDTH >= window_h:
        tile_size = window_h / immap.size[1]
    else:
        tile_size = (window_w - MENU_WIDTH) / immap.size[0]

    tile_size = int(tile_size) if int(tile_size) >= 1 else 1 

def cordsConvert(cord: set | list | tuple, to_normal: bool = False):
    '''If to_normal is False will convert given cordinates to tile-cords. Else will do in reverse. Read notes on reverse.'''
    new_cord = []
    cord_type = type(cord)
    cord_list = []
    for check in cord:
        if type(check) == int:
            cord_list.append(cord)
            cord = cord_list
            break
    if to_normal == True:
        '''Does not give exact location of mouse, but rather starting location of tile (aka. top left corner). Unless provided tile cords are acurrate floates.'''
        for c in cord:
            c_type = type(c)
            c_clone = list(c)
            c_clone[0] = (c_clone[0] * tile_size) + grid_start
            c_clone[1] =  c_clone[1] * tile_size
            c_clone = c_type(c_clone)
            new_cord.append(c_clone)
    elif to_normal == False:
        for c in cord:
            c_type = type(c)
            c_clone = list(c)
            c_clone[0] = int((c_clone[0] - grid_start) / tile_size)
            c_clone[1] = int(c_clone[1] / tile_size)
            c_clone = c_type(c_clone)
            new_cord.append(c_clone)
    else:
        raise ValueError("Invalid value for to_normal!")

    new_cord = cord_type(new_cord[0])
    return new_cord

def mouseTilecords() -> None:
    '''Gets the position of the mouse and converts it to tile-cordinates'''
    global tile_cord_x, tile_cord_y, mouse_pos, mouse_tile_cords
    if mouse_pos[0] < grid_start:
        mouse_tile_cords = [0,0]
    mouse_pos = pygame.mouse.get_pos()
    mouse_tile_cords = cordsConvert(mouse_pos)
    tile_cord_x, tile_cord_y = mouse_tile_cords

def selectTiles():
    '''Takes care of the selecting of tiles and addding/removing them to/from the selected_tiles set and the apropriate bomb set'''
    global selection
    pos1, pos2 = selection
    x1, y1 = pos1
    x2, y2 = pos2
    if x2 > x1:
        x1, x2 = x2, x1
    if y2 > y1:
        y1, y2 = y2, y1
    converted_pos1 = cordsConvert((x1,y1), True) 
    converted_pos2 = cordsConvert((x2,y2), True)
    if converted_pos1[0] < grid_start or converted_pos1[1] >= grid_bottom or converted_pos2[1] >= grid_bottom:
        return None
    for x in range((x1 - x2)+1):
        x += x2
        for y in range((y1 - y2)+1):
            y += y2
            if (x,y) in selected_tiles:
                selected_tiles.remove((x,y))
                if (x,y) in active_bomb.tiles:
                    active_bomb.tiles.remove((x,y))
                else:
                    for bomb in Bomb.instances.values():
                        if not (x,y) in bomb.tiles:
                            continue
                        bomb.tiles.remove((x,y))
            else:
                selected_tiles.add((x, y))
                active_bomb.tiles.add((x,y))

def drawStartMenu():
    global launch_btn, mapselect_btn
    screen.fill(colors["all"]["background"])
    menu_btn_font = pygame.font.SysFont("Cooper Black", 40)
    menu_btn_color = colors["start_menu"]["button-background"]

    launch_btn_size = (300, 50)
    launch_btn_location = center(launch_btn_size[0], launch_btn_size[1], window_w, window_h, "both")
    launch_btn = Button(menu_btn_color, launch_btn_location[0], launch_btn_location[1], launch_btn_size[0], launch_btn_size[1], "Launch!", menu_btn_font, colors["start_menu"]["button-font"], insta_draw=True)

    mapselect_btn_size = launch_btn_size
    mapselect_btn_location = (launch_btn_location[0], launch_btn_location[1] + 80)
    mapselect_btn = Button(menu_btn_color, mapselect_btn_location[0], mapselect_btn_location[1], mapselect_btn_size[0], mapselect_btn_size[1], "Map selection", menu_btn_font, colors["start_menu"]["button-font"], insta_draw=True)

def drawMapSelect():
    global mapdict, back_button, map_queue_x_buttons_dict, map_launch_btn
    screen.fill(colors["all"]["background"])
    MapFrame.instance_num = 0
    MapFrame.row = 0
    back_button = RoundButton(colors["all"]["back_button"]["stage1"], 20, 20, 30, 30, "<", standard_font,colors["all"]["back_button"]["font1"],[colors["all"]["back_button"]["border1"], "3"], insta_draw = True)

    mapdir = os.path.join(SELF_LOC + '/resources/maps')
    mapdict = {}
    for map in os.listdir(mapdir):
        file_ending = re.search(r".*(\..*)$", map).group(1)
        if not file_ending == ".png":
            continue 
        mapdict[map] = MapFrame(colors["map_select"]["map-frame"], os.path.join(mapdir, map), map.removesuffix(file_ending))
    
    #region Map queue
    map_queue_x_buttons_dict = {}
    map_queue_element_height = 50
    def draw_map_queue_element(top_y: int, mapname: str):
        pygame.draw.rect(screen, colors["map_select"]["queue"]["element"]["border"], [5, top_y, map_queue_w - 10, map_queue_element_height], 1)
        mapname_text_font = standard_font
        mapname_text = mapname.rpartition('_')[0]
        mapname_ftext = mapname_text_font.render(mapname_text, True, colors["map_select"]["queue"]["element"]["text"])
        mapname_width, mapname_height = mapname_ftext.get_size()
        mapname_y = top_y + center(item_height = mapname_height, parent_height = 50, center_direction = "vertical")
        screen.blit(mapname_ftext, [10, mapname_y])

        # X button
        x_text_font = standard_font
        x_ftext = x_text_font.render("x", True, (0,0,0)) #color does not matter
        x_ftext_width, x_ftext_height = x_ftext.get_size()
        x_ftext_y =  top_y + center(item_height = x_ftext_height, parent_height = 50, center_direction = "vertical")
        map_queue_x_buttons_dict[mapname] = Button(colors["all"]["background"], map_queue_w - 15 - x_ftext_width, x_ftext_y, x_ftext_width, x_ftext_height, "x", x_text_font,  colors["map_select"]["queue"]["element"]["x-button"], insta_draw = True)
    
    pygame.draw.line(screen, colors["map_select"]["queue"]["line"], [map_queue_w, 0], [map_queue_w, window_h], 2)

    top_y = 100
    for map in map_queue:
        draw_map_queue_element(top_y, map)
        top_y += map_queue_element_height + 5
    #endregion

    map_launch_btn_size = (190, 50)
    map_launch_btn_x, map_launch_btn_y = center(item_width = map_launch_btn_size[0], parent_width = map_queue_w, center_direction="horizontal"), window_h - map_launch_btn_size[1] - 5
    map_launch_btn = Button(colors["map_select"]["launch_btn"]["stage1"], map_launch_btn_x, map_launch_btn_y, map_launch_btn_size[0], map_launch_btn_size[1], "Launch!", standard_font,colors["map_select"]["launch_btn"]["font1"], insta_draw=True)

def drawGrid():
    '''Used to draw base grid before effects'''
    screen.fill(colors["all"]["background"])

    pix_x, pix_y = 0,0
    pxmap = immap.load()
    for x in range(grid_start, immap.size[0]*tile_size + grid_start, tile_size):
        for y in range(0, immap.size[1]*tile_size, tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            pygame.draw.rect(screen, pxmap[pix_x,pix_y], rect)
            pygame.draw.rect(screen, colors["game"]["grid-border"], rect, 1)
            pix_y += 1
        pix_x += 1
        pix_y = 0

def drawMenu():
    global bomb1_btn, bomb2_btn, bomb3_btn, explode_btn, next_map_btn
    pygame.draw.rect(screen,colors["all"]["background"], pygame.Rect(0, 0, MENU_WIDTH, window_h))
    #region BombButton drawing
    bomb_button_y_pos = 30
    for bomb_button in BombButton.instances.values():
        bomb_button.x_pos = 20
        bomb_button.y_pos = bomb_button_y_pos
        bomb_button.width = 100
        bomb_button.height = 50

        bomb_button.draw()
        bomb_button_y_pos += 60
    
    #endregion
    if time.time() >= explode_time + max(Bomb.explode_durations):
        explode_btn = Button(colors["game"]["explode_btn"]["stage1"], 10, window_h - 90, 150, 50, "EXPLODE!", standard_font,colors["game"]["explode_btn"]["font1"],[colors["game"]["explode_btn"]["border1"] ,3, 4], insta_draw=True)
    else:
        explode_btn = Button(colors["game"]["explode_btn"]["stage2"], 10, window_h - 90, 150, 50, "EXPLODE!", standard_font,colors["game"]["explode_btn"]["font2"],[colors["game"]["explode_btn"]["border2"] ,3, 4], insta_draw=True)
    
    next_map_btn = Button(colors["game"]["next_map_btn"]["stage1"], 10, window_h - 150, 150, 50, "Next map", standard_font,colors["game"]["next_map_btn"]["font1"],[colors["game"]["next_map_btn"]["border1"] ,3, 4], insta_draw=True)

    # draw active-bomb text
    active_bomb_font = standard_font
    active_bomb_font_color = colors["game"]["active_bomb-font"]
    active_bomb_ftext = active_bomb_font.render(active_bomb_text, True, active_bomb_font_color)
    pygame.draw.rect(screen, colors["all"]["background"], [0, window_h-30, 190, 30])
    screen.blit(active_bomb_ftext, (20, window_h - 20))
    # draw score text
    total_score_font = active_bomb_font
    total_score_font_color = colors["game"]["total_score-font"]
    total_score_ftext = total_score_font.render(f"Score:{total_score}", True, total_score_font_color)
    screen.blit(total_score_ftext, (20, window_h - 200))

def drawEfects():
    #hover efect
    if mouse_pos[0] > grid_start and mouse_pos[1] < immap.size[1] * tile_size:
        hover_Surface = pygame.Surface((tile_size, tile_size))
        hover_Surface.set_alpha(128)
        hover_Surface.fill(colors["game"]["grid-hover"])
        blit_x, blit_y = cordsConvert(mouse_tile_cords, True)
        screen.blit(hover_Surface,(blit_x, blit_y))
    #clicked efects
    for bomb in Bomb.instances.values():
        bomb.draw()
    #explosions of bombs
    current_time = time.time()
    for bomb in Bomb.instances.values():
        bomb.explode(current_time)
    

def registerScoreParameter(function):
    score_functions.add(function)

def calculateTotalScore():
    score = 0
    for value in score_functions:
        score += value()
    return score

@registerScoreParameter
def tilesHitScore():
    all_tiles_hit = set()
    for bomb in Bomb.instances.values():
        all_tiles_hit.update(bomb.explosion_area)
    houses_hit = mapcolors[(255, 0, 255)]  & all_tiles_hit
    industry_hit = mapcolors[(255, 0, 0)]  & all_tiles_hit
    houses_value = len(houses_hit) * 200
    industry_value = len(industry_hit) * 50
    return industry_value - houses_value

class Bomb(abc.ABC):
    '''This is the abc that all bombs should inherit from'''
    instances = {}
    explode_durations = []
    def __init__(self, radius, explode_duration, tile_icon: tuple | pygame.Surface, explosion_color, key:str, nickname:str, create_button = True) -> None:
        self.key = key
        self.nickname = nickname
        self.radius = radius
        if type(tile_icon) == str:
            self.tile_icon = strtoRGB(tile_icon)
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
    def __init__(self, radius, explode_duration, tile_icon: tuple | pygame.Surface, key:str, nickname:str) -> None:
        super().__init__(radius, explode_duration, tile_icon, colors["game"]["bombs"]["conventional"]["explosion-area"], key, nickname)

    def draw(self):
        if type(self.tile_icon) == tuple:
            for loc in self.tiles:
                real_loc = cordsConvert(loc, True)
                rect = pygame.Rect(real_loc[0], real_loc[1], tile_size, tile_size)
                pygame.draw.rect(screen, self.tile_icon, rect)
        elif type(self.tile_icon) == pygame.Surface:
            for loc in self.tiles:
                real_loc = cordsConvert(loc, True)
                tile_icon_scaled = pygame.transform.scale(self.tile_icon, (tile_size, tile_size))
                screen.blit(tile_icon_scaled, (real_loc[0], real_loc[1]))
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

    def explode(self, current_t):
        if not current_t - self.explode_duration <= explode_time or self.tiles == set():
            return None
        for explosion_effect in self.explosion_area:
            real_loc = cordsConvert(explosion_effect, True)
            pygame.draw.rect(screen, self.explosion_color, pygame.Rect(real_loc[0], real_loc[1],tile_size,tile_size))

class Button:
    def __init__(self, color ,x_pos: int, y_pos: int, width:int, height: int, text: str, font, font_color, border: typing.Literal["color","width","radius"]= None, insta_draw: bool = False) -> None:
        self.color = strtoRGB(color)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.font_Color = strtoRGB(font_color)
        self.ftext = self.font.render(text, True, font_color)
        if not border == None:
            self.border = border
            self.border[0] = strtoRGB(self.border[0])
            self.border[1] = int(self.border[1])
            self.border[2] = int(self.border[2])

        if insta_draw == True:
            self.draw()

    def draw(self) -> None:
        pygame.draw.rect(screen, self.color, [self.x_pos, self.y_pos, self.width,self.height])
        if hasattr(self, "border"):
            pygame.draw.rect(screen, self.border[0], [self.x_pos - (self.border[1] / 2), self.y_pos - (self.border[1] / 2), self.width + self.border[1],self.height + self.border[1]], self.border[1], self.border[2])
        self.text_width  = self.ftext.get_width()
        self.text_height = self.ftext.get_height()
        self.text_centered_x = self.x_pos + center(item_width = self.text_width, parent_width = self.width, center_direction = 'horizontal')
        self.text_centered_y = self.y_pos + center(item_height = self.text_height, parent_height = self.height, center_direction = 'vertical')
        screen.blit(self.ftext, (self.text_centered_x, self.text_centered_y))

    def checkmouseover(self) -> bool:
        if self.x_pos <= mouse_pos[0] <= self.x_pos + self.width and self.y_pos <= mouse_pos[1] <= self.y_pos + self.height:
            return True
        else:
            return False

class RoundButton(Button):
    """Draws a button as an ellipse"""
    def __init__(self, color, x_pos: int, y_pos: int, width: int, height: int, text: str, font, font_color, border: typing.Literal['color', 'width'] = None, insta_draw: bool = False) -> None:
        super().__init__(color, x_pos, y_pos, width, height, text, font, font_color, [*border, 0], insta_draw)
        
        # math from https://stackoverflow.com/questions/59971407/how-can-i-test-if-a-point-is-in-an-ellipse
        self.semi_axis_a = self.width // 2
        self.semi_axis_b = self.width // 2
        self.scale_y = self.semi_axis_a / self.semi_axis_b
        self.cpt_x, self.cpt_y = self.x_pos + self.width / 2, self.y_pos + self.height / 2 

    def draw(self) -> None:
        pygame.draw.ellipse(screen, self.color, [self.x_pos, self.y_pos, self.width,self.height])
        if hasattr(self, "border"):
            pygame.draw.ellipse(screen, self.border[0], [self.x_pos - (self.border[1] / 2), self.y_pos - (self.border[1] / 2), self.width + self.border[1],self.height + self.border[1]], self.border[1])
        self.text_width  = self.ftext.get_width()
        self.text_height = self.ftext.get_height()
        self.text_centered_x = self.x_pos + center(item_width = self.text_width, parent_width = self.width, center_direction = 'horizontal')
        self.text_centered_y = self.y_pos + center(item_height = self.text_height, parent_height = self.height, center_direction = 'vertical')
        screen.blit(self.ftext, (self.text_centered_x, self.text_centered_y))

    def checkmouseover(self) -> bool:
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
        super().__init__(colors["game"]["bomb-buttons"]["conventional"]["stage1"], x_pos, y_pos, width, height, text,standard_font,colors["game"]["bomb-buttons"]["conventional"]["font1"], insta_draw = insta_draw)
        self.bombinstance = bombinstance

    def onclick(self):
        global active_bomb_text, active_bomb
        active_bomb_text = self.bombinstance.nickname
        active_bomb = Bomb.instances[self.bombinstance.key]

    def checkAndExecute(self):
        if super().checkmouseover():
            self.onclick()

class MapFrame:
    row = 0
    instance_num = 0
    def __init__(self, frame_color, map_path: str, instance_name) -> None:
        MapFrame.instance_num += 1
        self.size = 200
        self.instance_name = instance_name
        self.x_pos, self.y_pos= self._get_pos()
        self.frame_color = strtoRGB(frame_color)
        self.map_path = map_path
        
        self.draw()
    
    def _get_pos(self):
        instance_num = MapFrame.instance_num
        row = 0
        while instance_num > map_row_lengh:
            instance_num -= map_row_lengh
            row += 1    
            
        cords = [instance_num, row]
        converted_cords = [map_queue_w + 20 + (20 + self.size) * cords[0], 20 + (20 + self.size) * cords[1]]
        return converted_cords

    def draw(self):
        frame = pygame.Rect(self.x_pos, self.y_pos, self.size, self.size)
        map_preview = pygame.image.load(self.map_path)
        map_preview = pygame.transform.scale(map_preview, (160, 160))
        pygame.draw.rect(screen, self.frame_color, frame)
        screen.blit(map_preview, (self.x_pos + 20, self.y_pos + 20))
    
    def checkmouseover(self) -> bool:
        if self.x_pos <= mouse_pos[0] <= self.x_pos + self.size and self.y_pos <= mouse_pos[1] <= self.y_pos + self.size:
            return True
        else:
            return None

    def onclick(self):
        map_queue.append(f"{self.instance_name}_{uuid.uuid4()}")

    def checkANDExecute(self) -> None:
        if self.checkmouseover() == True:
            self.onclick()
if __name__=="__main__":
    with open('color.json') as json_file:
        colors = json.load(json_file)
    SELF_LOC = os.path.dirname(os.path.realpath(__file__))
    MENU_WIDTH = 200
    selected_tiles = set()
    explode_time = 1
    FPS = 60
    map_queue_w = 200
    main()