from os.path import join
from time import sleep
import shared
from utils.gamestage_enum import GameStage
from pygame import mixer
from threading import Thread

muted = False


def toggle_mute() -> None:
    global muted
    if mixer.music.get_busy():
        mixer.music.pause()
        muted = True
    else:
        mixer.music.play()
        muted = False


def _fade_song() -> None:
    if mixer.music.get_busy():
        mixer.music.fadeout(200)
        sleep(2)


def __song_daemon_internal() -> None:
    last_stage = None
    while True:
        if muted:
            continue

        if last_stage == shared.stage and mixer.music.get_busy():
            continue

        if last_stage == shared.stage:
            mixer.music.play()
            continue

        match (shared.stage):
            case GameStage.START:
                _fade_song()
                mixer.music.load(join("..", "assets", "music", "menu-music.wav"))
                mixer.music.play()
            case GameStage.GAME:
                _fade_song()
                mixer.music.load(join("..", "assets", "music", "game-music.wav"))
                mixer.music.play()

        last_stage = shared.stage


def song_daemon_init():
    daemon = Thread(target=__song_daemon_internal, daemon=True)
    daemon.start()
