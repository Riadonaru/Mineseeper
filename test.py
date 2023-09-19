import pygame
from pygame.locals import *
from globals import PATH

pygame.init()
screen = pygame.display.set_mode((500, 500), RESIZABLE)
pic = pygame.image.load(PATH + "hourglass.png")  # You need an example picture in the same folder as this file!
running = True
while running:
    pygame.event.pump()
    event = pygame.event.wait()
    if event.type == QUIT:
        running = False
    elif event.type == VIDEORESIZE:
        screen.blit(pygame.transform.scale(pic, event.dict['size']), (0, 0))
        pygame.display.update()
    elif event.type == VIDEOEXPOSE:  # handles window minimising/maximising
        screen.fill((0, 0, 0))
        screen.blit(pygame.transform.scale(pic, screen.get_size()), (0, 0))
        pygame.display.update()