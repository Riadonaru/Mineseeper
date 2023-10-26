import pygame
from playsound import playsound

from globals import (BG_COLOR, BLACK, BLUE, CELL_EDGE, DISP, FONTS, LRB_BORDER,
                     SETTINGS, SOUNDS, WHITE)


class Textbox(pygame.Rect):
    
    box_left = LRB_BORDER * 9
    box_height = CELL_EDGE / 2
    box_width = 55 * SETTINGS["scale"]

    def __init__(self, name: str, top, left = box_left, height = box_height) -> None:
        self.name = name.capitalize().replace("_", " ")
        self.active = False
        self.color = BLUE
        self.text = str(SETTINGS[name])
        self.max_chars = len(self.text)
        self.font = pygame.font.Font(FONTS + "Font.ttf", int(CELL_EDGE / 2))
        super().__init__(left, top, len(self.text) * 25 * SETTINGS["scale"], height)


    def text_handler(self, key: int, unicode):
        if self.active:
            if key == pygame.K_BACKSPACE and len(self.text) > 0:
                self.text = ""
            elif key != pygame.K_BACKSPACE and self.max_chars >= len(self.text):
                self.text += unicode
            else:
                if SETTINGS["play_sounds"]:
                    playsound(SOUNDS + "error.mp3", False)


    def draw(self):
        if self.active:
            self.color = BLUE
        else:
            self.color = BG_COLOR
        pygame.draw.rect(DISP, self.color, self)
        text = self.font.render(self.name.replace("_", " "), 0, BLACK)
        text_surface = self.font.render(self.text, True, WHITE)
        DISP.blit(text, (LRB_BORDER, self.top))
        DISP.blit(text_surface, (self.x, self.y))