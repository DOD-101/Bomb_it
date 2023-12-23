"""
The main file of the "Bomb it" game.

Status: Working
"""


import time
import os
import re
import json

import pygame
pygame.init()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import shared
shared.init()

from PIL import Image

from utils import utils
from utils.gamestage_enum import GameStage
from utils.selecttiles import selectTiles
from utils.bombplacement import clearBombs, placeBombs
from components.bombs import Bomb, ConventionalBomb
from components.buttons import Button, BombButton
from components.mapframe import MapFrame
from components.score import calculateTotalScore, saveScore
from utils.map_utils import px_to_colordict
from render.draw import Draw

def main():
    global  mouse_pos, selection, explode_time # should not be global anymore
    # pygame.init()
    pygame.display.set_caption("Bomb It!")

    # Bombs
    kt10_img = pygame.image.load(os.path.join('..', 'assets', 'bomb_icons', 'conventional', '10kt.png')).convert()
    Bomb.instances["kt10"] = ConventionalBomb(shared.screen, 0, 2, kt10_img, "kt10", "G-kt10", 10)
    kt50_img = pygame.image.load(os.path.join('..', 'assets', 'bomb_icons', 'conventional', '50kt.png')).convert()
    Bomb.instances["kt50"] = ConventionalBomb(shared.screen, 2, 2, kt50_img, "kt50", "G-kt50", 150)
    kt100_img = pygame.image.load(os.path.join('..', 'assets', 'bomb_icons', 'conventional', '100kt.png')).convert()
    Bomb.instances["kt100"] = ConventionalBomb(shared.screen, 5, 2, kt100_img, "kt100", "G-kt100", 600)

    #-----
    shared.active_bomb = list(Bomb.instances.values())[0]

    total_score = 100

    first_run = True
    draw_grid = True

    draw_background_grid = False

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
                    if Button.instances["maplaunch"].checkmouseover(mouse_pos):
                        shared.stage = GameStage.GAME
                        shared.gameVars(first = True)
                        draw_grid = True
                        clearBombs()
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

            if draw_background_grid == True:
                # Technically this makes it possible to click on a button on the Game "screen" in the same frame
                # This issue however is almost impossible to run into
                draw_grid = True
                draw_background_grid = False
                shared.stage = GameStage.SCORE

            if draw_grid:
                sDraw.drawGrid()
                sDraw.drawTileIcons()
                grid_area = (shared.grid_start, 0, shared.window_w - shared.grid_start, shared.window_h - (shared.window_h - shared.grid_bottom))
                grid_surface = pygame.Surface([shared.window_w - shared.grid_start, shared.window_h - (shared.window_h - shared.grid_bottom)])
                grid_surface.blit(shared.screen, [0,0], grid_area)
                draw_grid = False
            else:
                shared.screen.fill(shared.COLORS["all"]["background"])
                shared.screen.blit(grid_surface, [shared.grid_start, 0])

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
                        saveScore(total_score, shared.map_queue[0])
                        explode_time = time.time()

                    if Button.instances["nextmap"].checkmouseover(mouse_pos):
                        shared.map_queue.nextMap()

                        draw_grid = True
                        shared.gameVars()
                        clearBombs()

                    if Button.instances["score"].checkmouseover(mouse_pos):
                        shared.stage = GameStage.SCORE

                if event.type == pygame.MOUSEBUTTONDOWN and mouse_pos[0] > shared.MENU_WIDTH and selecting == False:
                    selecting = True
                    selection = list()
                    selection.append((mouse_tile_cords[0], mouse_tile_cords[1]))

                if event.type == pygame.MOUSEBUTTONUP and selecting == True and event.button in [1,3]:
                    selecting = False
                    selection.append((mouse_tile_cords[0], mouse_tile_cords[1]))
                    if time.time() >= explode_time + max(Bomb.explode_durations):
                        if event.button == 1:
                            shared.active_bomb.tiles = selectTiles(selection, shared.active_bomb)
                        elif event.button == 3:
                            shared.active_bomb.tiles = selectTiles(selection, shared.active_bomb, remove = True)

                if event.type == pygame.VIDEORESIZE:
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)
                    draw_grid = True
                    continue
        if shared.stage == GameStage.SCORE:
            sDraw.drawScoreScreen()
            from utils.utils import center
            main_backdrop_cords = center(shared.window_w / 2.5, shared.window_h / 1.2, shared.window_w, shared.window_h, "both")
            box = (main_backdrop_cords[0], main_backdrop_cords[1], main_backdrop_cords[0] + shared.window_w / 2.5, main_backdrop_cords[1] + shared.window_h / 1.2)
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    shared.stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not box[0] <= mouse_pos[0] <= box[2] or not box[1] <= mouse_pos[1] <= box[3]:
                        shared.stage = GameStage.GAME

                    # select page buttons
                    for key, page_btn in Button.instances.items():
                        reresult = re.search(r'page_btn_(\d+)', key)
                        if reresult:
                            if page_btn.checkmouseover(mouse_pos):
                                sDraw.score_page = int(reresult.group(1))

                    # bomb place buttons
                    for key, place_button in Button.instances.items():
                        reresult = re.search(r'bomb_place_(\d+)', key)
                        if reresult:
                            if place_button.checkmouseover(mouse_pos):
                                with open(os.path.join('..', 'userdata', 'scores.json'), 'r') as json_file:
                                    SCORES: dict = json.load(json_file)
                                # gets the proper dict of bomb cords -- possible since the num in the name of the button is the same as in the scores.json
                                placeBombs(SCORES[shared.map_queue[0].split('_')[0]][re.search(r'\d+', key).group()][2])
                                shared.stage = GameStage.GAME

                if event.type == pygame.VIDEORESIZE:
                    shared.stage = GameStage.GAME
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)
                    draw_background_grid = True
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