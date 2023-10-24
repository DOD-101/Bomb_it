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
from utils.clearbombs import clearBombs
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
    kt10_img = pygame.image.load(os.path.join('..', 'assets', 'bomb_icons', 'conventional', '10kt.png')).convert()
    Bomb.instances["kt10"] = ConventionalBomb(shared.screen, 0, 2,kt10_img, "kt10", "G-kt10", 10)
    kt50_img = pygame.image.load(os.path.join('..', 'assets', 'bomb_icons', 'conventional', '50kt.png')).convert()
    Bomb.instances["kt50"] = ConventionalBomb(shared.screen, 2, 2, kt50_img, "kt50", "G-kt50", 150)
    kt100_img = pygame.image.load(os.path.join('..', 'assets', 'bomb_icons', 'conventional', '100kt.png')).convert()
    Bomb.instances["kt100"] = ConventionalBomb(shared.screen, 5, 2, kt100_img, "kt100", "G-kt100", 600)

    #-----
    shared.active_bomb = list(Bomb.instances.values())[0]

    total_score = 100

    first_run = True

    selecting = False
    game_clock = pygame.time.Clock()
    while shared.stage != GameStage.QUIT:
        mouse_pos = pygame.mouse.get_pos()
        if shared.stage == GameStage.START:
            sDraw.drawStartMenu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shared.stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if Button.instances["launch"].checkmouseover(mouse_pos):
                        shared.stage = GameStage.GAME

                    if Button.instances["mapselect"].checkmouseover(mouse_pos):
                        shared.stage = GameStage.MAP_SELECT

                if event.type == pygame.VIDEORESIZE:
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)
                    continue

        if shared.stage == GameStage.MAP_SELECT:

            sDraw.drawMapSelect()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shared.stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if Button.instances["maplaunch"] .checkmouseover(mouse_pos):
                        shared.stage = GameStage.GAME
                        break

                    for map in MapFrame.instances.keys():
                        MapFrame.instances[map].checkANDExecute(mouse_pos)

                    for x_button in sDraw.map_queue_x_buttons_dict.keys():
                        if sDraw.map_queue_x_buttons_dict[x_button].checkmouseover(mouse_pos):
                            shared.map_queue.remove(x_button)

                    if Button.instances["mapback"].checkmouseover(mouse_pos):
                        shared.stage = GameStage.START

                if event.type == pygame.VIDEORESIZE:
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)

                    continue

        if shared.stage == GameStage.GAME:
            if first_run:
                shared.gameVars(first=True)
            first_run = False

            mouse_tile_cords = utils.mouseTilecords()
            sDraw.drawGrid(shared.immap, shared.grid_start)
            sDraw.drawEfects(mouse_pos, mouse_tile_cords, explode_time)
            sDraw.drawMenu(explode_time, total_score)
            # event handling, gets all events from the event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shared.stage = GameStage.QUIT
                    break


                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if Button.instances["back"].checkmouseover(mouse_pos):
                        shared.stage = GameStage.START

                    for bomb_button in BombButton.instances.values():
                        bomb_button.checkAndExecute(mouse_pos)

                    if Button.instances["clear"].checkmouseover(mouse_pos):
                        clearBombs()

                    if Button.instances["explode"].checkmouseover(mouse_pos) and time.time() >= explode_time + max(Bomb.explode_durations):
                        for bomb in Bomb.instances.values():
                            bomb.calculateAreas()
                        total_score = calculateTotalScore()
                        explode_time = time.time()

                    if Button.instances["nextmap"].checkmouseover(mouse_pos):
                        if len(shared.map_queue) != 0:
                            del shared.map_queue[0]

                        shared.gameVars()
                        clearBombs()

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