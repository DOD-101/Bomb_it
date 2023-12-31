"""
Implements the startExplosion function to trigger at the start of any
explosion of the bombs. Currently only responsible for sound.

Status: Working
"""
from random import choice
from time import sleep

from pygame import mixer

from components.bombs import Bomb


def startExplosion():
    """
    Run at the start of every explosion of the bombs
    (aka. when the explosion button is pressed) to
    play the explosion sounds.
    """
    all_bombs = list(Bomb.instances.values())

    amount_to_sounds = {}
    for bomb in all_bombs:
        len_bomb_tiles = len(bomb.tiles)
        if len_bomb_tiles != 0:
            amount_to_sounds[len_bomb_tiles] = bomb.sounds

    for key, value in amount_to_sounds.items():
        for _ in range(key if key < 10 else 10):
            explosion_sound = mixer.Sound(choice(value))
            explosion_sound.play()
            sleep(0.15)
