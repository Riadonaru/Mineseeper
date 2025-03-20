import pygame

class Component(pygame.Rect):
    
    def __init__(self, rect: pygame.Rect, name: str = "") -> None:
        self.name = name
        self.active = False
        self.visible = True
        super().__init__(rect)
        return super().__init_subclass__()
    
    def __manage__(self):
        pass

    def __draw__(self):
        pass