from math import ceil
from os import path, chdir
from random import choice
from time import sleep

from pygame import mixer

from components.bombs import Bomb


def startExplosion():
    all_bombs =  list(Bomb.instances.values())

    amount_to_sounds = {}
    for bomb in all_bombs:
        len_bomb_tiles = len(bomb.tiles)
        if len_bomb_tiles != 0:
            amount_to_sounds[len_bomb_tiles] = bomb.sounds
    for key, value in amount_to_sounds.items():
        for _ in range(key if key < 10 else 10):
            __startExplosion_inner(choice(value))
            sleep(0.15)

def __startExplosion_inner(sound_path: str):
    explosion_sound = mixer.Sound(sound_path)
    explosion_sound.play()