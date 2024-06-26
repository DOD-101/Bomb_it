"""
The main file of the "Bomb it" game.

Status: Working
"""

import os
import re
import time
from json import load
from threading import Thread

import pygame

import shared
from components.bombs import Bomb, ClusterBomb, ConventionalBomb
from components.buttons import BombButton, Button
from components.explosion import startExplosion
from components.mapframe import MapFrame
from components.score import calculateTotalScore, saveScore, score_functions
from components.musicplayer import song_daemon_init, toggle_mute
from render.draw import Draw
from utils import utils
from utils.bombplacement import clearBombs, placeBombs
from utils.gamestage_enum import GameStage
from utils.selecttiles import selectTiles

pygame.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
shared.init()
shared.score_functions = score_functions

FPS = 60  # config file or shared.py


def main():
    """The main function for running the game.
    Should not be called from anywhere outside of main.py."""
    # pygame.init()
    pygame.display.set_caption("Bomb It!")
    explode_time = 1  # shared.py ?

    # Bombs
    kt10_img = pygame.image.load(
        os.path.join("..", "assets", "bomb_icons", "conventional", "10kt.png")
    ).convert()
    Bomb.instances["kt10"] = ConventionalBomb(
        shared.screen, 0, 2, kt10_img, "kt10", "G-kt10", 10
    )
    kt50_img = pygame.image.load(
        os.path.join("..", "assets", "bomb_icons", "conventional", "50kt.png")
    ).convert()
    Bomb.instances["kt50"] = ConventionalBomb(
        shared.screen, 2, 2, kt50_img, "kt50", "G-kt50", 150
    )
    kt100_img = pygame.image.load(
        os.path.join("..", "assets", "bomb_icons", "conventional", "100kt.png")
    ).convert()
    Bomb.instances["kt100"] = ConventionalBomb(
        shared.screen, 5, 2, kt100_img, "kt100", "G-kt100", 600
    )

    c5_img = pygame.image.load(
        os.path.join("..", "assets", "bomb_icons", "cluster", "5c.png")
    ).convert()
    Bomb.instances["c5"] = ClusterBomb(shared.screen, 5, 80, 2, c5_img, "c5", "C-5", 60)
    c10_img = pygame.image.load(
        os.path.join("..", "assets", "bomb_icons", "cluster", "10c.png")
    ).convert()
    Bomb.instances["c10"] = ClusterBomb(
        shared.screen, 10, 80, 2, c10_img, "c10", "C-10", 100
    )
    # -----
    shared.active_bomb = list(Bomb.instances.values())[0]

    total_score = 100

    first_run = True
    draw_grid = True

    draw_background_grid = False

    selecting = False
    game_clock = pygame.time.Clock()
    frame = 0
    song_daemon_init()
    while shared.stage != GameStage.QUIT:
        mouse_pos = pygame.mouse.get_pos()
        if shared.stage == GameStage.START:
            sDraw.drawStartMenu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shared.stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if Button.instances["launch"].checkMouseOver(mouse_pos):
                        shared.stage = GameStage.GAME

                    if Button.instances["mapselect"].checkMouseOver(mouse_pos):
                        shared.stage = GameStage.MAP_SELECT

                    if Button.instances["mute"].checkMouseOver(mouse_pos):
                        print("called")
                        toggle_mute()

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
                    if Button.instances["maplaunch"].checkMouseOver(mouse_pos):
                        shared.stage = GameStage.GAME
                        shared.gameVars(first=True)
                        draw_grid = True
                        clearBombs()
                        break

                    for map_item in MapFrame.instances.values():
                        map_item.checkANDExecute(mouse_pos)

                    for (
                        x_button_key,
                        x_button,
                    ) in sDraw.map_queue_x_buttons_dict.items():
                        if x_button.checkMouseOver(mouse_pos):
                            shared.map_queue.remove(x_button_key)

                    if Button.instances["mapback"].checkMouseOver(mouse_pos):
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

            if draw_background_grid:
                # Technically this makes it possible to click on a button
                # on the Game "screen" in the first frame.
                # This issue however is almost impossible to run into.
                draw_grid = True
                draw_background_grid = False
                shared.stage = GameStage.SCORE

            if draw_grid:
                sDraw.drawGrid()
                sDraw.drawTileIcons()
                grid_area = (
                    shared.grid_start,
                    0,
                    shared.window_w - shared.grid_start,
                    shared.window_h - (shared.window_h - shared.grid_bottom),
                )
                grid_surface = pygame.Surface(
                    [
                        shared.window_w - shared.grid_start,
                        shared.window_h - (shared.window_h - shared.grid_bottom),
                    ]
                )
                grid_surface.blit(shared.screen, [0, 0], grid_area)
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
                    if Button.instances["back"].checkMouseOver(mouse_pos):
                        shared.stage = GameStage.START

                    for bomb_button in BombButton.instances.values():
                        bomb_button.checkAndExecute(mouse_pos)

                    if Button.instances["clear"].checkMouseOver(mouse_pos):
                        clearBombs()

                    if Button.instances["explode"].checkMouseOver(
                        mouse_pos
                    ) and time.time() >= explode_time + max(Bomb.explode_durations):
                        for bomb in Bomb.instances.values():
                            bomb.calculateAreas()
                        total_score = calculateTotalScore()
                        saveScore(total_score, shared.map_queue[0])
                        Thread(target=startExplosion).start()
                        explode_time = time.time()

                    if Button.instances["nextmap"].checkMouseOver(mouse_pos):
                        shared.map_queue.nextMap()

                        draw_grid = True
                        shared.gameVars()
                        clearBombs()

                    if Button.instances["score"].checkMouseOver(mouse_pos):
                        shared.stage = GameStage.SCORE

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and mouse_pos[0] > shared.MENU_WIDTH
                    and not selecting
                ):
                    selecting = True
                    selection = []
                    selection.append((mouse_tile_cords[0], mouse_tile_cords[1]))

                if (
                    event.type == pygame.MOUSEBUTTONUP
                    and selecting
                    and event.button in [1, 3]
                ):
                    selecting = False
                    selection.append((mouse_tile_cords[0], mouse_tile_cords[1]))
                    if time.time() >= explode_time + max(Bomb.explode_durations):
                        if event.button == 1:
                            shared.active_bomb.tiles = selectTiles(
                                selection, shared.active_bomb
                            )
                        elif event.button == 3:
                            shared.active_bomb.tiles = selectTiles(
                                selection, shared.active_bomb, remove=True
                            )

                if event.type == pygame.VIDEORESIZE:
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)
                    draw_grid = True
                    continue
        if shared.stage == GameStage.SCORE:
            sDraw.drawScoreScreen()

            main_backdrop_cords = utils.center(
                shared.window_w / 2.5,
                shared.window_h / 1.2,
                shared.window_w,
                shared.window_h,
                "both",
            )
            box = (
                main_backdrop_cords[0],
                main_backdrop_cords[1],
                main_backdrop_cords[0] + shared.window_w / 2.5,
                main_backdrop_cords[1] + shared.window_h / 1.2,
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shared.stage = GameStage.QUIT
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (
                        not box[0] <= mouse_pos[0] <= box[2]
                        or not box[1] <= mouse_pos[1] <= box[3]
                    ):
                        shared.stage = GameStage.GAME

                    # select page buttons
                    for key, page_btn in Button.instances.items():
                        reresult = re.search(r"page_btn_(\d+)", key)
                        if reresult:
                            if page_btn.checkMouseOver(mouse_pos):
                                sDraw.score_page = int(reresult.group(1))

                    # bomb place buttons
                    for key, place_button in Button.instances.items():
                        reresult = re.search(r"bomb_place_(\d+)", key)
                        if reresult:
                            if place_button.checkMouseOver(mouse_pos):
                                with open(
                                    os.path.join("..", "userdata", "scores.json"),
                                    "r",
                                    encoding="utf-8",
                                ) as json_file:
                                    scores: dict = load(json_file)
                                # gets the proper dict of bomb cords
                                # possible since the num in the name of the button
                                # is the same as in the scores.json
                                placeBombs(
                                    scores[shared.map_queue[0].split("_")[0]][
                                        re.search(r"\d+", key).group()
                                    ][2]
                                )
                                shared.stage = GameStage.GAME

                if event.type == pygame.VIDEORESIZE:
                    shared.stage = GameStage.GAME
                    shared.onWindowScale(event)
                    sDraw.updateSurface(shared.screen)
                    draw_background_grid = True
        # at the end of every frame
        shared.rscreen.blit(shared.screen, (0, 0))
        pygame.display.flip()
        frame += 1
        print(frame, end="\r")
        game_clock.tick(FPS)


sDraw = Draw(shared.screen)  # sDraw for screenDraw
if __name__ == "__main__":
    # SELF_LOC = os.path.dirname(os.path.realpath(__file__))
    main()
