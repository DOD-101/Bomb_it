import pygame
import pygame_widgets as pyw

import threading
import abc
import time
import os
import typing
import math

from colorama import Fore, init
from PIL import Image
init()

SELF_LOC = os.path.dirname(os.path.realpath(__file__))
window_w = 1000
window_h = 300
MENU_WIDTH = 200
selected_tiles = set()
explode_time = 1
FPS = 60
score_types = {}
total_score = 100
# define a main function
def main():
    global screen, mouse_pos, active_bomb_text, active_bomb, selection, kt10, kt50, kt100, explode_time, window_w, window_h
    pygame.init()
    pygame.display.set_caption("Bomb It!")

    gettilesize() #!!TEMP

    screen = pygame.Surface((window_w, window_h))
    rscreen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)
    # Bombs
    kt10_img = pygame.image.load(os.path.join(SELF_LOC, "resources\\bomb_icons\\conventional\\test.png")).convert()
    kt10  = ConventionalBomb(0, 3,kt10_img, "kt10", "G-kt10")
    kt50  = ConventionalBomb(5, 3,(255, 102, 255), "kt50", "G-kt50")
    kt100 = ConventionalBomb(10, 3,(102, 255, 102), "kt100", "G-kt100")

    #-----
    active_bomb_text = '10 kT'
    active_bomb = kt10

    selecting = False
    game_clock = pygame.time.Clock()
    mouse_pos = pygame.mouse.get_pos()
    mousetilecords()
    start_menu_running = True
    game_running = True
    while start_menu_running:
        drawstartmenu()
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running, start_menu_running = False, False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if launch_btn.checkmouseover():
                    start_menu_running = False
            
            if event.type == pygame.VIDEORESIZE:
                onwindowscale(event)
                continue

        rscreen.blit(screen, (0,0))
        pygame.display.flip()


    while game_running:
        gettilesize()
        drawGrid()
        drawEfects()
        drawMenu()
        mouse_pos = pygame.mouse.get_pos()
        threading.Thread(target=mousetilecords).start()
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bomb1_btn.check_execute()
                bomb2_btn.check_execute()
                bomb3_btn.check_execute()
                
                if explode_btn.checkmouseover():
                    explode_time = time.time()
                
                if mouse_pos[0] > MENU_WIDTH and selecting == False:
                    selecting = True
                    selection = list()
                    selection.append((tile_cord_x, tile_cord_y))
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and selecting == True:
                selecting = False
                selection.append((tile_cord_x, tile_cord_y))
                selecttiles()

            if event.type == pygame.VIDEORESIZE:
                onwindowscale(event)
                continue

        rscreen.blit(screen, (0,0))
        pygame.display.flip()
        
        game_clock.tick(FPS)

def onwindowscale(event):
    global screen, rscreen, window_w, window_h
    window_w, window_h = event.size
    rscreen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)
    screen = pygame.transform.scale(screen, (window_w, window_h))
    screen.fill((0,0,0))
    
    gettilesize()
    print(tile_size)

def gettilesize():
    global tile_size
    immap = Image.open("resources\maps\map0.png")
    pxmap = immap.load()
    if window_w - MENU_WIDTH >= window_h:
        tile_size = window_h / immap.size[1]
    else:
        tile_size = window_w / immap.size[0]
    
    tile_size = int(tile_size)

def strtoRGB(colorStr: str) -> tuple:
    if type(colorStr) == str: 
        colorStr = colorStr.lower()
        match(colorStr):
            case('white'):
                colorStr = (255,255,255)
            case('black'):
                colorStr = (0,0,0)
            case('red'):
                colorStr = (255,0,0)
            case('green'):
                colorStr = (0,255,0)
            case('blue'):
                colorStr = (0,0,255)
            case('armygreen'):
                colorStr = (75, 83, 32)
            case('explosionorange'):
                colorStr = (255, 102, 0)
            case(_):
                raise ValueError(f"Color str:{colorStr} doesn't exist!")
    return colorStr

def center(item_width: float | int = 0, item_height: float | int = 0, parent_width: float | int = 0, parent_height: float | int = 0, center_direction: typing.Literal["horizontal", "vertical", "both"] = "both"):
    def horizontal():
        return ((parent_width - item_width) / 2)
    def vertical():
        return ((parent_height - item_height) / 2)
    
    match(center_direction):
        case("horizontal"):
            return horizontal()
        case("vertical"):
            return vertical()
        case("both"):
            return (horizontal(), vertical())
        case(_):
            raise ValueError(f"{center_direction} is an invalid value for center_direction")

def cordsconvert(cord: set | list | tuple, to_normal: bool = False):
    '''If to_normal is False will convert given cordinates to tile-cords. Else will do in reverse. Read notes on reverse.'''
    new_cord = type(cord)
    if to_normal == True:
        '''Does not give exact location of mouse, but rather starting location of tile (aka. top left corner). Unless provided tile cords are acurrate floates.'''
        if type(cord) == set or type(cord) == list:
            for c in cord:
                c[0] = (c[0] * tile_size) + MENU_WIDTH
                c[1] =  c[1] * tile_size
                new_cord.add(c)
        elif type(cord) == tuple:
            x = (cord[0] * tile_size) + MENU_WIDTH
            y = cord[1] * tile_size
            new_cord = tuple([x,y])
        else:
            raise TypeError(f"Invalid type to convert! Type {type(cord)} not supported.")
    elif to_normal == False:
        if type(cord) == set or type(cord) == list:
            for c in cord:
                c[0] = int((c[0] - MENU_WIDTH) / tile_size)
                c[1] =  int(c[1] / tile_size)
                new_cord.add(c)
        elif type(cord) == tuple:
            x = int((cord[0] - MENU_WIDTH) / tile_size)
            y = int(cord[1] / tile_size)
            new_cord = tuple([x,y])
        else:
            raise TypeError(f"Invalid type to convert! Type {type(cord)} not supported.")
    else:
        raise ValueError("Invalid value for to_normal!")

    return new_cord

def mousetilecords() -> None:
    '''Gets the position of the mouse and converts it to tile-cordinates'''
    global tile_cord_x, tile_cord_y, mouse_pos, mouse_tile_cords
    if mouse_pos[0] < MENU_WIDTH:
        mouse_tile_cords = [0,0]
    mouse_pos = pygame.mouse.get_pos()
    mouse_tile_cords = cordsconvert(mouse_pos)
    tile_cord_x, tile_cord_y = mouse_tile_cords

def selecttiles():
    '''Takes care of the selecting of tiles and addding/removing them to/from the selected_tiles set and the apropriate bomb set'''
    global selection
    pos1, pos2 = selection
    x1, y1 = pos1
    x2, y2 = pos2
    if x2 > x1:
        x1, x2 = x2, x1
    if y2 > y1:
        y1, y2 = y2, y1
    
    for x in range((x1 - x2)+1):
        x += x2 
        for y in range((y1 - y2)+1):
            y += y2
            if (x,y) in selected_tiles: 
                selected_tiles.remove((x,y))
                if (x,y) in active_bomb.tiles:
                    active_bomb.tiles.remove((x,y))
                else:
                    for key, value in Bomb.instances.items():
                        if not (x,y) in eval(key).tiles:
                            continue
                        eval(key).tiles.remove((x,y))
            else:
                selected_tiles.add((x, y))
                active_bomb.tiles.add((x,y))

def drawstartmenu():
    global launch_btn
    menu_btn_font = pygame.font.SysFont("Cooper Black", 40)
    menu_btn_color = (102, 153, 153)

    launch_btn_size = (300, 50)
    launch_btn_location = center(launch_btn_size[0], launch_btn_size[1], window_w, window_h, "both")
    launch_btn = Button(menu_btn_color, launch_btn_location[0], launch_btn_location[1], launch_btn_size[0], launch_btn_size[1], "Launch!", menu_btn_font,"white", instaDraw=True)

    mapselect_btn_size = launch_btn_size
    mapselect_btn_location = (launch_btn_location[0], launch_btn_location[1] + 80)
    mapselect_btn = Button(menu_btn_color, mapselect_btn_location[0], mapselect_btn_location[1], mapselect_btn_size[0], mapselect_btn_size[1], "Map selection", menu_btn_font, "white", instaDraw=True)

def drawGrid():
    '''Used to draw base grid before effects'''
    immap = Image.open("resources\maps\map0.png")
    pxmap = immap.load()
    pix_x, pix_y = 0,0
    for x in range(MENU_WIDTH, immap.size[0]*tile_size + MENU_WIDTH, tile_size):
        for y in range(0, immap.size[1]*tile_size, tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            pygame.draw.rect(screen, pxmap[pix_x,pix_y], rect)
            pygame.draw.rect(screen, (255,255,255), rect, 1)
            pix_y += 1
        pix_x += 1
        pix_y = 0

def drawMenu():
    global bomb1_btn, bomb2_btn, bomb3_btn, explode_btn
    pygame.draw.rect(screen, strtoRGB('black'), pygame.Rect(0, 0, MENU_WIDTH, window_h))
    bomb1_btn = BombButton(20, 30, 100, 50,'10kT', kt10)
    bomb2_btn = BombButton(20, 90, 100, 50,'50kT', kt50)
    bomb3_btn = BombButton(20, 150, 100, 50,'100kT', kt100)
    explode_btn = Button('red', 10, window_h -100, 150, 50, 'EXPLODE!', pygame.font.SysFont('Bahnschrift SemiBold', 30),'black',[ 'white',3, 4], instaDraw=True)
    # draw active-bomb text
    active_bomb_font = pygame.font.SysFont('Bahnschrift SemiBold', 30)
    active_bomb_font_color = strtoRGB('white')
    active_bomb_ftext = active_bomb_font.render(active_bomb_text, True, active_bomb_font_color)
    pygame.draw.rect(screen, (0,0,0), [0, window_h-30, 190, 30])
    screen.blit(active_bomb_ftext, (20, window_h - 20))
    # draw score text
    total_score_font = active_bomb_font
    total_score_font_color = active_bomb_font_color
    total_score_ftext = total_score_font.render(f"Score:{total_score}", True, total_score_font_color)
    pygame.draw.rect(screen, (0,0,0), [0, window_h - 200, 190, 30])
    screen.blit(total_score_ftext, (20, window_h - 200))

def drawEfects():
    #hover efect
    if mouse_pos[0] > MENU_WIDTH:
        hover_Surface = pygame.Surface((tile_size, tile_size))
        hover_Surface.set_alpha(128)
        hover_Surface.fill((255,0,0))
        blit_x, blit_y = cordsconvert(mouse_tile_cords, True)
        screen.blit(hover_Surface,(blit_x, blit_y))
    #clicked efects
    for key, value in Bomb.instances.items():
        eval(key).draw()
    #explosions of bombs
    current_time = time.time()
    for key, value in Bomb.instances.items():
        explode_func = getattr(eval(key), "explode")
        explode_func(current_time)

def register_score_parameter(value: int, name, group = False):
    value = round(value)
    score_types[name] = [value]

def calculate_total_score():
    score = 0
    for key, value in score_types.items():
        score += value[0]
 
class Bomb(abc.ABC):
    instances = {}
    '''This is the abc that all bombs should inherit from'''
    def __init__(self, radius, explode_duration, tile_icon: tuple | pygame.Surface, explosion_color, instance_name:str, nickname:str = "No nickname") -> None:
        self.instance_name = instance_name
        self.nickname = nickname
        self.radius = radius * tile_size
        if type(tile_icon) == str: 
            self.tile_icon = strtoRGB(tile_icon)
        else:
            self.tile_icon = tile_icon
        self.tiles = set()
        self.explode_duration = explode_duration
        self.explosion_color = explosion_color

        Bomb.instances[self.instance_name] = [self.__class__.__name__, self.instance_name,self.nickname]

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def explode(self):
        pass

class ConventionalBomb(Bomb):
    def __init__(self, radius, explode_duration, tile_icon: tuple | pygame.Surface, instance_name:str, nickname:str = "No nickname") -> None:
        super().__init__(radius, explode_duration, tile_icon, strtoRGB('explosionorange'), instance_name, nickname)

    def draw(self):
        if type(self.tile_icon) == tuple:
            for loc in self.tiles:
                real_loc = cordsconvert(loc, True)
                rect = pygame.Rect(real_loc[0], real_loc[1], tile_size, tile_size)
                pygame.draw.rect(screen, self.tile_icon, rect)
        elif type(self.tile_icon) == pygame.Surface:
            for loc in self.tiles:
                real_loc = cordsconvert(loc, True)
                tile_icon_scaled = pygame.transform.scale(self.tile_icon, (tile_size, tile_size))
                screen.blit(tile_icon_scaled, (real_loc[0], real_loc[1]))
        else:
            raise TypeError(f"Invalid type '{type(self.tile_icon)}' for self.tile_icon")

    def explode(self, current_t):
        if not current_t - self.explode_duration <= explode_time:
            return None
        for loc in self.tiles:
            real_loc = cordsconvert(loc, True)
            Exp_rect = pygame.Rect(real_loc[0]-self.radius, real_loc[1]-self.radius,(self.radius*2)+1*tile_size,(self.radius*2)+1*tile_size)
            pygame.draw.rect(screen, strtoRGB('explosionorange'), Exp_rect)
        
class Button():
    def __init__(self, color ,x_pos: int, y_pos: int, width:int, height: int, text: str, font, font_color, border: list = None, instaDraw: bool = False) -> None:
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

        if instaDraw == True:
            self.draw()
    
    def draw(self) -> None:
        pygame.draw.rect(screen, self.color, [self.x_pos, self.y_pos, self.width,self.height])
        if hasattr(self, "border"):
            pygame.draw.rect(screen, self.border[0], [self.x_pos - (self.border[1] / 2), self.y_pos - (self.border[1] / 2), self.width + self.border[1],self.height + self.border[1]], self.border[1], self.border[2])
        self.text_width  = self.ftext.get_width()
        self.text_height = self.ftext.get_height()
        self.text_centered_x = ((self.width - self.text_width) / 2) + self.x_pos
        self.text_centered_y = ((self.height - self.text_height) / 2) + self.y_pos
        screen.blit(self.ftext, (self.text_centered_x, self.text_centered_y))

        
    def checkmouseover(self) -> bool:
        if self.x_pos <= mouse_pos[0] <= self.x_pos + self.width and self.y_pos <= mouse_pos[1] <= self.y_pos + self.height:
            return True
        else:
            return False

class BombButton(Button):
    '''Use this class to make any BomButtons so that they all have certain atributes the same'''
    def __init__(self, x_pos: int, y_pos: int, width: int, height: int, text: str, bombinstance: type[Bomb]) -> None:
        super().__init__('armygreen', x_pos, y_pos, width, height, text,pygame.font.SysFont('Bahnschrift SemiBold', 30),'black', instaDraw=True)
        self.bombinstance = bombinstance
    
    def onclick(self):
        global active_bomb_text, active_bomb
        active_bomb_text = self.text
        active_bomb = self.bombinstance


    
    def check_execute(self):
        if super().checkmouseover():
            self.onclick()


if __name__=="__main__":
    main()