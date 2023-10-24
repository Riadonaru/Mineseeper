import pygame

from globals import DISP, DISP_H, DISP_W, SETTINGS


class Button(pygame.Rect):
    def __init__(self, image_path: str):
        image = pygame.image.load(image_path).convert_alpha()
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image.convert_alpha(), (int(
            width * SETTINGS["scale"]), int(height * SETTINGS["scale"])))
        self.clicked = False
        super().__init__((DISP_W - width) // 2, (DISP_H - height) // 2, width, height)

    def draw(self):
        DISP.blit(self.image, (self.x, self.y))