import pygame

from globals import BLACK, CELL_EDGE, DISP, FONTS, LRB_BORDER, SETTINGS, WHITE

pygame.font.init()

class Checkbox(pygame.Rect):
     
    def __init__(self, name: str, top, left=LRB_BORDER):
        super().__init__(left, top, 12 * SETTINGS["scale"], 12 * SETTINGS["scale"])
        self.font = pygame.font.Font(FONTS + "Font.ttf", int(CELL_EDGE / 2))
        self.active = False
        self.name = None
        self.name = name.capitalize().replace("_", " ")
        self.active = SETTINGS[name]


    def draw(self):
        pygame.draw.rect(DISP, WHITE, self)
        pygame.draw.rect(DISP, BLACK, self, 1)
        if self.active:
            pygame.draw.circle(DISP, BLACK, (self.x + self.width / 2, self.y + self.width / 2), 4 * SETTINGS["scale"])
