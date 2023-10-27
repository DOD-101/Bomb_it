"""
Implements functions needed for scoring.

Status: Working
"""
import shared
import json
import os
import datetime
from components.bombs import Bomb

def registerScoreParameter(function):
    shared.score_functions.add(function)

def calculateTotalScore():
    total_score = 0
    for func in shared.score_functions:
        score, key = func()
        total_score += score
        shared.score_parts[key] = score

    return total_score

def saveScore(score: int | float, map_name: str) -> list:
    """
    Saves the score and the current date and time in an array in scores.json
    Returns the array, which it saved.
    """
    with open(os.path.join('..', 'userdata', 'scores.json'), 'r') as json_file:
        SCORES = json.load(json_file)

    map_name = map_name.split('_')[0]

    if not map_name in SCORES.keys():
        SCORES[map_name] = {}

    key = len(SCORES[map_name])

    time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    SCORES[map_name][key] = [score, time]

    json_object = json.dumps(SCORES, indent=4)

    with open(os.path.join('..', 'userdata', 'scores.json'), 'w') as json_file:
        json_file.write(json_object)

    return SCORES[map_name][key]

@registerScoreParameter
def tilesHitScore():
    all_tiles_hit = set()
    for bomb in Bomb.instances.values():
        all_tiles_hit.update(bomb.explosion_area)
    total = 0
    for tile in shared.TILES:
        try:
            total += len(set(shared.mapcolors[tuple(shared.TILES[tile]["color"])])  & all_tiles_hit) * shared.TILES[tile]["score"]
        except KeyError:
            pass # this just means a map doesn't contain a certain tile
    return total, "Tiles Hit"

@registerScoreParameter
def bombPrices():
    total_price = 0
    for bomb in Bomb.instances.values():
        total_price -= bomb.price * len(bomb.tiles)
    return total_price, "Bomb Cost"