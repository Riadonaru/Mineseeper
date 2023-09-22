import pygame

from globals import CELL_EDGE, DISP, BLACK, LRB_BORDER, PATH, SETTINGS, WHITE
pygame.font.init()

class Checkbox(pygame.Rect):
     
    def __init__(self, top, left=LRB_BORDER):
        super().__init__(left, top, 12 * SETTINGS["scale"], 12 * SETTINGS["scale"])
        self.font = pygame.font.Font(PATH + "Font.ttf", int(CELL_EDGE / 2))
        self.active = False
        self.name = None


    def draw(self):
        pygame.draw.rect(DISP, WHITE, self)
        pygame.draw.rect(DISP, BLACK, self, 1)
        if self.active:
            pygame.draw.circle(DISP, BLACK, (self.x + self.width / 2, self.y + self.width / 2), 4 * SETTINGS["scale"])

    def populate_box(self, name: str):
        self.name = name
        self.active = SETTINGS[name.lower()]
