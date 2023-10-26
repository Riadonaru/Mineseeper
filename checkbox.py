import pygame

from globals import BLACK, CELL_EDGE, DISP, FONTS, LRB_BORDER, SETTINGS, WHITE


class Checkbox(pygame.Rect):
     
    def __init__(self, name: str, top, left=LRB_BORDER):
        super().__init__(left, top, 12 * SETTINGS["scale"], 12 * SETTINGS["scale"])
        self.font = pygame.font.Font(FONTS + "Font.ttf", int(CELL_EDGE / 2))
        self.active = False
        self.name = None
        self.name = name.capitalize().replace("_", " ")
        self.active = SETTINGS[name]


    def draw(self):
        text = self.font.render(self.name.replace("_", " "), 0, BLACK)
        DISP.blit(text, (LRB_BORDER + self.left * 1.5, self.top))
        pygame.draw.rect(DISP, WHITE, self)
        pygame.draw.rect(DISP, BLACK, self, 1)
        if self.active:
            pygame.draw.circle(DISP, BLACK, (self.x + self.width / 2, self.y + self.width / 2), 4 * SETTINGS["scale"])
