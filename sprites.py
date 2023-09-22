import pygame

from globals import BG_COLOR, IMAGES, LOSE, SETTINGS, WIN


class Spritesheet(object):

    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()

        
    def get_image(self, x, y, width, height, scale: int = 1):
        image = pygame.Surface((width, height)).convert_alpha()
        image.fill(BG_COLOR)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(BG_COLOR)
        return image

    def load_sprites(self):

        sprites = [self.get_image(x * 34 + 1, 1, 34, 34, SETTINGS["scale"]) for x in range(20)]
        sprites.insert(WIN, self.get_image(1, 35, 300, 222))
        sprites.insert(LOSE, self.get_image(301, 35, 300, 222))
        return sprites

SPRITES = Spritesheet(IMAGES + "spritesheet.png").load_sprites()
