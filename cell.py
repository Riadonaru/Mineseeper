import pygame

from globals import CELL, CELL_EDGE, DISP, FLAG, LRB_BORDER, TOP_BORDER
from sprites import SPRITES


class Cell():
    
    def __init__(self, x: int = 0, y: int = 0, value: int = 0, hidden: bool = True, create_hitbox: bool = False) -> None:
        self.__hidden: bool = hidden
        self.__flagged: bool = False
        self.__content: int = value
        self.x: int = x
        self.y: int = y
        if create_hitbox:
            self.create_hitbox()

    @property
    def hidden(self) -> bool:
        return self.__hidden

    @hidden.setter
    def hidden(self, __value):
        if self.flagged:
            print("Can't dehide a flagged cell")
        else:
            self.__hidden = __value

    @property
    def flagged(self) -> bool:
        return self.__flagged

    @flagged.setter
    def flagged(self, __value: bool) -> None:
        if self.hidden:
            self.__flagged = __value
        else:
            print("Can't flag a revealed cell")

    @property
    def value(self) -> int:
        return self.__content

    @value.setter
    def value(self, __value) -> None:
        self.__content = __value

    
    def data(self):
        if self.hidden:
            if self.flagged:
                return -3
            return -2
        return self.__content

    def create_hitbox(self):
        self.hitbox = pygame.Rect(LRB_BORDER + self.x * CELL_EDGE,
                                TOP_BORDER + self.y * CELL_EDGE, CELL_EDGE, CELL_EDGE)

    def draw(self) -> None:
        """This method draws a cell onto the display
        """
        if self.hidden:
            DISP.blit(SPRITES[FLAG if self.flagged else CELL], self.hitbox)
        else:
            DISP.blit(SPRITES[self.value], self.hitbox)
