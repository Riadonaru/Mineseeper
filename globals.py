import json
from typing import Dict

import pygame

PATH = __file__[:-10]
SOUNDS = PATH + "sounds/"
FONTS = PATH + "fonts/"
IMAGES = PATH + "images/"

with open(PATH[:-6] + "settings.json", "r") as stngs:
    SETTINGS: Dict[str, any] = json.loads(stngs.read())

BLACK = (0, 0, 0)
BLUE = (173, 216, 230)
BG_COLOR = (192, 192, 192)
WHITE = (255, 255, 255)

PREVIOUS = False
CURRENT = False
SETTING: bool = False

CELL: int = -5
FLAG: int = -4
CLICKED_MINE: int = -3
NOMINE: int = -2
MINE: int = -1
SMILE: int = 9
SHOCKED: int = 10
COOL: int = 11
DEAD: int = 12

PLAYING: int = 1
PAUSED: int = 2
SET: int = 3
WIN: int = 15
LOSE: int = 16

GEAR: int = 13
RESET: int = SMILE

HOURGLASS: int = 14

CELL_EDGE: int = 34 * SETTINGS["scale"]
TOP_BORDER: int = 100 * SETTINGS["scale"]
LRB_BORDER: int = 16 * SETTINGS["scale"]

FONT_SIZE = int(16 * SETTINGS["scale"])
PAUSE_FONT_SIZE = int(40 * SETTINGS["scale"])

HOST = SETTINGS["server_data"]["host"]  # The server's hostname or IP address
PORT = SETTINGS["server_data"]["port"]  # The port used by the server
MAX_MSG_LEN = 2048
MAX_RETRIES = 3

DISP_W = CELL_EDGE * SETTINGS["width"] + LRB_BORDER * 2
DISP_H = CELL_EDGE * SETTINGS["height"] + LRB_BORDER + TOP_BORDER

DISP = pygame.display.set_mode((DISP_W, DISP_H))
pygame.display.set_caption("Minesweeper")
