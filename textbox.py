import pygame
from globals import DISP, DISP_H, DISP_W, PATH, LRB_BORDER, CELL_EDGE, SETTINGS
import sys
from playsound import playsound

class Textbox():

    def __init__(self) -> None:
        self.rect = pygame.Rect(LRB_BORDER, DISP_H - CELL_EDGE // 2 - LRB_BORDER, DISP_W - LRB_BORDER * 2, CELL_EDGE // 2)
        self.text = ""
        self.active_color = (0, 0, 0)
        self.passive_color = (200, 200, 200)
        self.displayed_color = self.passive_color
        self.font = pygame.font.Font(PATH + "Font.ttf", CELL_EDGE // 2)
        self.active = False

    def draw(self):
        if self.active:
            self.displayed_color = self.active_color
        else:
            self.displayed_color = self.passive_color
        pygame.draw.rect(DISP, self.displayed_color, self.rect)
        if len(self.text) > SETTINGS["width"] * 2:
            self.text = self.text[:-1]
            playsound(PATH + "music/error.mp3", False)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        DISP.blit(text_surface, (self.rect.x, self.rect.y))