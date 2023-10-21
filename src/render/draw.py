"""NOT USED"""
from src import shared
import pygame

class Draw:
    def __init__(self, screen) -> None:
        self.screen = screen

    def drawGrid(self, map_image, tile_size):
        '''Used to draw base grid before effects'''
        self.screen.fill(shared.colors["all"]["background"])

        pix_x, pix_y = 0,0
        pxmap = map_image.load()
        for x in range(grid_start, map_image.size[0]*tile_size + grid_start, tile_size):
            for y in range(0, map_image.size[1]*tile_size, tile_size):
                rect = pygame.Rect(x, y, tile_size, tile_size)
                pygame.draw.rect(screen, pxmap[pix_x,pix_y], rect)
                pygame.draw.rect(screen, shared.colors["game"]["grid-border"], rect, 1)
                pix_y += 1
            pix_x += 1
            pix_y = 0

        return self.screen