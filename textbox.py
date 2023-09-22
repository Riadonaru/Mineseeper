import re
from typing import Tuple
import pygame
from globals import DISP, PATH, LRB_BORDER, CELL_EDGE, BLUE, WHITE, BG_COLOR, SETTINGS
from playsound import playsound


class Textbox():
    
    box_left = LRB_BORDER * 9
    box_height = CELL_EDGE / 2
    box_width = 55 * SETTINGS["scale"]

    def __init__(self, top, left = box_left, width = box_width, height = box_height) -> None:
        self.text = ""
        self.name = None
        self.active = False
        self.max_chars = (width - width % 25) / 25
        self.rect = pygame.Rect(left, top, width, height)
        self.font = pygame.font.Font(PATH + "Font.ttf", int(CELL_EDGE / 2))
        self.color = BLUE

    def text_handler(self, key: int, unicode):
        if self.active:
            if key == pygame.K_BACKSPACE and len(self.text) > 0:
                self.text = ""
            elif key != pygame.K_BACKSPACE and self.max_chars >= len(self.text):
                self.text += unicode
            else:
                if SETTINGS["play_sounds"]:
                    playsound(PATH + "music/error.mp3", False)

    def populate_box(self, name: str):
        self.name = name
        self.text = str(SETTINGS[name.lower()])


    def draw(self):
        if self.active:
            self.color = BLUE
        else:
            self.color = BG_COLOR
        pygame.draw.rect(DISP, self.color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        DISP.blit(text_surface, (self.rect.x, self.rect.y))