import pygame

import threading
import abc
import time
import os

from colorama import Fore, init
init()

SELF_LOC = os.path.dirname(os.path.realpath(__file__))
WINDOW_HEIGHT = 1100
WINDOW_WIDTH = WINDOW_HEIGHT
MENU_WIDTH = 200
tile_size = 20
selected_tiles = set()
explode_time = 1
FPS = 60

# define a main function
def main():
    global screen, mouse_pos, active_bomb_text, active_bomb, selection, kt10, kt50, kt100, explode_time
    pygame.init()
    pygame.display.set_caption("Bomb It!")
     
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # Bombs
    kt10_img = pygame.image.load(os.path.join(SELF_LOC, "resources\\bomb_icons\\conventional\\test.png")).convert()
    kt10  = ConventionalBomb(0, 3,kt10_img, "kt10", "G-kt10")
    kt50  = ConventionalBomb(5, 3,(255, 102, 255), "kt50", "G-kt50")
    kt100 = ConventionalBomb(10, 3,(102, 255, 102), "kt100", "G-kt100")

    #-----
    running = True
    active_bomb_text = '10 kT'
    active_bomb = kt10

    selecting = False
    game_clock = pygame.time.Clock()
    mouse_pos = pygame.mouse.get_pos()
    mousetilecords()
    while running:
        drawGrid()
        drawEfects()
        drawMenu()
        mouse_pos = pygame.mouse.get_pos()
        threading.Thread(target=mousetilecords).start()
        drawactivebombtext()
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
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
        
        game_clock.tick(FPS)
        pygame.display.update()

def drawGrid():
    '''Used to draw base grid before effects'''
    for x in range(MENU_WIDTH, WINDOW_WIDTH, tile_size):
        for y in range(0, WINDOW_HEIGHT, tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            pygame.draw.rect(screen, (102, 102, 102), rect)
            pygame.draw.rect(screen, (255,255,255), rect, 1)

def drawMenu():
    global bomb1_btn, bomb2_btn, bomb3_btn, explode_btn
    pygame.draw.rect(screen, strtoRGB('black'), pygame.Rect(0, 0, MENU_WIDTH, WINDOW_HEIGHT))
    bomb1_btn = BombButton(20, 30, 100, 50,'10kT', kt10)
    bomb2_btn = BombButton(20, 90, 100, 50,'50kT', kt50)
    bomb3_btn = BombButton(20, 150, 100, 50,'100kT', kt100)
    explode_btn = Button('red', 10, WINDOW_HEIGHT -100, 150, 50, 'EXPLODE!', pygame.font.SysFont('Bahnschrift SemiBold', 30),'black',[ 'white',3, 4], instaDraw=True)

def drawactivebombtext():
    font = pygame.font.SysFont('Bahnschrift SemiBold', 30)
    font_color = strtoRGB('white')
    ftext = font.render(active_bomb_text, True, font_color)
    pygame.draw.rect(screen, (0,0,0), [0, WINDOW_HEIGHT-30, 190, 30])
    screen.blit(ftext, (20, WINDOW_HEIGHT - 20))

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

def cordsconvert(cord: set | list | tuple, to_normal: bool = False):
    '''If to_normal is False will convert given cordinates to tile-cords. Else will do in reverse. Reade notes on reverse.'''
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
                c[0] = int(c[0] / tile_size) - int(MENU_WIDTH / tile_size)
                c[1] =  int(c[1] / tile_size)
                new_cord.add(c)
        elif type(cord) == tuple:
            x = int(cord[0] / tile_size) - int(MENU_WIDTH / tile_size)
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
        return None
    mouse_pos = pygame.mouse.get_pos()
    mouse_tile_cords = cordsconvert(mouse_pos)
    tile_cord_x, tile_cord_y = mouse_tile_cords

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
                screen.blit(self.tile_icon, (real_loc[0], real_loc[1]))
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