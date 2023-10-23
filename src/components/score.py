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
    houses_hit = shared.MAPCOLORS[(255, 0, 255)]  & all_tiles_hit
    industry_hit = shared.MAPCOLORS[(255, 0, 0)]  & all_tiles_hit
    houses_value = len(houses_hit) * 200
    industry_value = len(industry_hit) * 50
    return industry_value - houses_value