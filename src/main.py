"""
The main file of the "Bomb it" game.

Status: Working
"""


import time
import os
import re
import random

import pygame
pygame.init()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import shared
shared.init()

from PIL import Image

from utils import utils
from utils.gamestage_enum import GameStage
from utils.selecttiles import selectTiles
from components.bombs import Bomb, ConventionalBomb
from components.buttons import Button, BombButton
from components.mapframe import MapFrame
from components.score import calculateTotalScore
from utils.map_utils import px_to_colordict
from render.draw import Draw

def main():
    global  mouse_pos, selection, explode_time
    # pygame.init()
    pygame.display.set_caption("Bomb It!")

    # Bombs
    kt10_img = pygame.image.load("..\\resources\\bomb_icons\\conventional\\test.png").convert()
    Bomb.instances["kt10"] = ConventionalBomb(shared.screen, 0, 3,kt10_img, "kt10", "G-kt10", 10)
    Bomb.instances["kt50"] = ConventionalBomb(shared.screen, 2, 3,(255, 102, 255), "kt50", "G-kt50", 200)
    Bomb.instances["kt100"] = ConventionalBomb(shared.screen, 5, 3,(102, 255, 102), "kt100", "G-kt100", 700)

    #-----
    shared.active_bomb = list(Bomb.instances.values())[0]

    total_score = 100

    stage = GameStage.START

    selecting = False
    game_clock = pygame.time.Clock()
    first_draw = True
    while stage != GameStage.QUIT:
        mouse_pos = pygame.mouse.get_pos()
        if stage == GameStage.START:
            sDraw.drawStartMenu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if Button.instances["launch"].checkmouseover(mouse_pos):
                        stage = GameStage.GAME

                    if Button.instances["mapselect"].checkmouseover(mouse_pos):
                        stage = GameStage.MAP_SELECT

                if event.type == pygame.VIDEORESIZE:
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)
                    continue

        if stage == GameStage.MAP_SELECT:

            sDraw.drawMapSelect()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if Button.instances["maplaunch"] .checkmouseover(mouse_pos):
                        stage = GameStage.GAME
                        break

                    for map in MapFrame.instances.keys():
                        MapFrame.instances[map].checkANDExecute(mouse_pos)

                    for x_button in sDraw.map_queue_x_buttons_dict.keys():
                        if sDraw.map_queue_x_buttons_dict[x_button].checkmouseover(mouse_pos):
                            shared.map_queue.remove(x_button)

                    if Button.instances["mapback"].checkmouseover(mouse_pos):
                        stage = GameStage.START

                if event.type == pygame.VIDEORESIZE:
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)

                    continue

        if stage == GameStage.GAME:
            if len(shared.map_queue) != 0:
                file_name = shared.map_queue[0].rpartition('_')[0] + ".png"
            elif first_draw:
                possible_maps = []
                for current_map in  os.listdir("..\\resources\maps"):
                    file_ending = re.search(r".*(\..*)$", current_map).group(1)
                    if not file_ending == ".png":
                        continue
                    possible_maps.append(current_map)
                file_name = possible_maps[random.randint(0, len(possible_maps) - 1)]


            immap = Image.open(os.path.join("..\\resources\maps", file_name)) # immap should not be defined here like this, only leads to problems
            shared.MAPCOLORS = px_to_colordict(immap, [(0, 255, 0),(0, 0, 255),(255, 0, 255),(255, 0, 0),(0,0,0),(255, 255, 0)]) # remove this as soon as possible
            mouse_tile_cords = utils.mouseTilecords()
            sDraw.drawGrid(immap, shared.grid_start)
            sDraw.drawEfects(mouse_pos, mouse_tile_cords, explode_time)
            sDraw.drawMenu(explode_time, total_score)
            first_draw = False
            # event handling, gets all events from the event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for bomb_button in BombButton.instances.values():
                        bomb_button.checkAndExecute(mouse_pos)

                    if Button.instances["explode"].checkmouseover(mouse_pos) and time.time() >= explode_time + max(Bomb.explode_durations):
                        for bomb in Bomb.instances.values():
                            bomb.calculateAreas()
                        total_score = calculateTotalScore()
                        explode_time = time.time()

                    if Button.instances["nextmap"].checkmouseover(mouse_pos):
                        if len(shared.map_queue) != 0:
                            del shared.map_queue[0]
                        else:
                            first_draw = True

                    if mouse_pos[0] > shared.MENU_WIDTH and selecting == False:
                        selecting = True
                        selection = list()
                        selection.append((mouse_tile_cords[0], mouse_tile_cords[1]))

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and selecting == True:
                    selecting = False
                    selection.append((mouse_tile_cords[0], mouse_tile_cords[1]))
                    if time.time() >= explode_time + max(Bomb.explode_durations):
                        shared.active_bomb.tiles = selectTiles(selection, shared.active_bomb)

                if event.type == pygame.VIDEORESIZE:
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)
                    continue

        # at the end of every frame
        shared.rscreen.blit(shared.screen, (0,0))
        pygame.display.flip()

        game_clock.tick(FPS)

sDraw = Draw(shared.screen) # sDraw for screenDraw
if __name__=="__main__":
    # SELF_LOC = os.path.dirname(os.path.realpath(__file__))
    explode_time = 1
    FPS = 60
    main()