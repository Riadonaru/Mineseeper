import pygame

from globals import CELL, CELL_EDGE, DISP, FLAG, LRB_BORDER, TOP_BORDER
from sprites import SPRITES


class Cell(pygame.Rect):

    def __init__(self, x: int = 0, y: int = 0, value: int = 0, hidden: bool = True) -> None:
        super().__init__(LRB_BORDER + x * CELL_EDGE,
                         TOP_BORDER + y * CELL_EDGE, CELL_EDGE, CELL_EDGE)
        self.x_index = x
        self.y_index = y
        self.adj_flags = 0
        self.__hidden: bool = hidden
        self.__flagged: bool = False
        self.__content: int = value

    @property
    def hidden(self) -> bool:
        return self.__hidden

    @hidden.setter
    def hidden(self, __value):
        if not self.flagged:
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

    def saturated(self):
        return self.adj_flags == self.value

    def data(self):
        if self.hidden:
            if self.flagged:
                return -3
            return -2
        return self.__content


    def draw(self) -> None:
        """This method draws a cell onto the display
        """
        if self.hidden:
            DISP.blit(SPRITES[FLAG if self.flagged else CELL], self)
        else:
            DISP.blit(SPRITES[self.value], self)
