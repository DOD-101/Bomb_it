"""
Implements functions needed for scoring.

Status: Working
"""
import shared
from components.bombs import Bomb

def registerScoreParameter(function):
    shared.score_functions.add(function)

def calculateTotalScore():
    score = 0
    for value in shared.score_functions:
        score += value()
    return score

@registerScoreParameter
def tilesHitScore():
    all_tiles_hit = set()
    for bomb in Bomb.instances.values():
        all_tiles_hit.update(bomb.explosion_area)
    total = 0
    for tile in shared.TILES:
        total += len(set(shared.mapcolors[tuple(shared.TILES[tile]["color"])])  & all_tiles_hit) * shared.TILES[tile]["score"]
    return total

@registerScoreParameter
def bombPrices():
    total_price = 0
    for bomb in Bomb.instances.values():
        total_price -= bomb.price * len(bomb.tiles)
    return total_price