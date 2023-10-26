import pygame

from globals import DISP, PAUSE_FONT_SIZE, FONTS, IMAGES, WHITE

pygame.font.init()

class Button(pygame.Rect):
    btn_left = pygame.image.load(IMAGES + "btn_left.png").convert_alpha()
    btn_right = pygame.image.load(IMAGES + "btn_right.png").convert_alpha()
    btn_back = pygame.image.load(IMAGES + "btn_back.png").convert_alpha()
    font = pygame.font.Font(FONTS + "Font.ttf", PAUSE_FONT_SIZE)

    def __init__(self, x, y, text: str):
        self.clicked = False
        self.text = Button.font.render(text, 0, WHITE)
        super().__init__(self.text.get_rect(center=(x, y)))

    def draw(self):
        height = Button.btn_back.get_height()
        for i in range(0, self.width + 16, 8):
            DISP.blit(Button.btn_back, (self.center[0] - self.width // 2 + i - 16, self.center[1] - height // 2))
        DISP.blit(Button.btn_left, (self.center[0] - self.width // 2 - 24, self.center[1] - height // 2))
        DISP.blit(Button.btn_right, (self.center[0] - self.width // 2 + self.width, self.center[1] - height // 2))
        DISP.blit(self.text, self)
