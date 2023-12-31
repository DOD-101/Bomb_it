"""
Implements functions needed for scoring.

Status: Working
"""
import datetime
import json
import os

import shared
from components.bombs import Bomb
from utils.scores_encoder import ScoresEncoder

score_functions = set()


def registerScoreParameter(function):
    """
    Used as a decorator to add every function to score_function
    Needs to be reworked.
    """
    score_functions.add(function)


def calculateTotalScore():
    """
    Uses the functions found in score functions to calculate the total score.
    Adds the return value (+ the total) of every function to shared.score_parts.
    """
    total_score = 0
    for func in score_functions:
        score, key = func()
        total_score += score
        shared.score_parts[key] = score

    return total_score


def saveScore(score: int | float, map_name: str) -> list:
    """
    Saves the score and the current date and time in an array in scores.json
    Returns the array, which it saved.
    """
    with open(
        os.path.join("..", "userdata", "scores.json"), "r", encoding="utf-8"
    ) as json_file:
        scores: dict = json.load(json_file)

    map_name = map_name.split("_")[0]

    if not map_name in scores.keys():
        scores[map_name] = {}

    key = len(scores[map_name])

    time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    scores[map_name][key] = [
        score,
        time,
        {key: list(bomb.tiles) for key, bomb in Bomb.instances.items()},
    ]

    json_object = ScoresEncoder.default(scores)

    with open(
        os.path.join("..", "userdata", "scores.json"), "w", encoding="utf-8"
    ) as json_file:
        json_file.write(json_object)

    return scores[map_name][key]


@registerScoreParameter
def tilesHitScore():
    """Calculates the score gained from the tiles hit."""
    all_tiles_hit = set()
    for bomb in Bomb.instances.values():
        all_tiles_hit.update(bomb.explosion_area)
    total = 0
    for tile in shared.TILES:
        try:
            total += (
                len(
                    set(shared.mapcolors[tuple(shared.TILES[tile]["color"])])
                    & all_tiles_hit
                )
                * shared.TILES[tile]["score"]
            )
        except KeyError:
            pass  # this just means a map doesn't contain a certain tile
    return total, "Tiles Hit"


@registerScoreParameter
def bombPrices():
    """Calculates the score lost from the price of the bombs used."""
    total_price = 0
    for bomb in Bomb.instances.values():
        total_price -= bomb.price * len(bomb.tiles)
    return total_price, "Bomb Cost"
