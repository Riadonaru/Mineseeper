import random
import threading

import numpy as np
from playsound import playsound

from cell import Cell
from globals import CLICKED_MINE, LOSE, MINE, NOMINE, PAUSED, SETTINGS, SOUNDS


class Grid():


    def __init__(self) -> None:
        self.clicked_cell: Cell = None
        self.state: int = PAUSED  # 1 for playing, 2 for paused, 3 for settings, 15 for win, 16 for lose.
        self.troll_mode: bool = False
        self.tiles = SETTINGS["width"] * SETTINGS["height"]
        self.mines = int(self.tiles * SETTINGS["mines%"] / 100)
        
        # Creating index values for mines
        self.temp = [-1 if i < self.mines else 0 for i in range(self.tiles)]
        random.shuffle(self.temp)
        self.temp = np.reshape(self.temp, (SETTINGS["height"], SETTINGS["width"]), 'F')

        # Populating the array with mines
        self.contents = np.ndarray((SETTINGS["height"], SETTINGS["width"])).astype(Cell)
        for x in range(SETTINGS["width"]):
            for y in range(SETTINGS["height"]):
                self.contents[y][x] = Cell(x, y, self.temp[y][x])

        if not SETTINGS["easy_start"]:
            self.init_cells()


    def troll(self):
        for y in range(SETTINGS["height"]):
            for x in range(SETTINGS["width"]):
                self.contents[y][x].value = random.randint(0, 20)

    def init_cells(self):
        for y in range(SETTINGS["height"]):
            for x in range(SETTINGS["width"]):
                self.assign_value(x, y)


    def easy_start(self, clicked_x: int, clicked_y: int):
        if not self.contents[clicked_y][clicked_x].flagged:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if self.contents[clicked_y + dy][clicked_x + dx].value == MINE:
                        x_new, y_new = self.find_clear_spot()
                        if x_new == -1 and y_new == -1:
                            self.troll_mode = True
                            self.troll()
                            return
                        self.contents[y_new][x_new].value = -1
                        self.contents[clicked_y+ dy][clicked_x + dx].value = 0

        self.init_cells()


    def find_clear_spot(self):
        for y in range(SETTINGS["height"]):
            for x in range(SETTINGS["width"]):
                if self.contents[y][x].value == 0:
                    return x, y

        return -1, -1

    def assign_value(self, x_index: int, y_index: int) -> int:
        """Initiates cell value and semi saturation.

        Args:
            x_index (int): The x index of the cell.
            y_index (int): The y index of the cell.
        """
        cell: Cell = self.contents[y_index][x_index]
        if cell.value != MINE:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if 0 <= x_index + dx < SETTINGS["width"] and 0 <= y_index + dy < SETTINGS["height"]:
                        adj_cell: Cell = self.contents[y_index + dy][x_index + dx]
                        if adj_cell.value == MINE:
                            cell.value += 1


    def reveal_next(self, x: int, y: int, first: bool = True): 
        """This method has the reveal algo. 
        """
        cell: Cell = self.contents[y][x]
        if not cell.flagged:
            if first:
                cell.hidden = False
            if cell.value == MINE:
                return self.reveal_all(cell)
            elif cell.saturated() and (first or (cell.hidden and not cell.flagged)):
                cell.hidden = False
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if 0 <= x + dx < SETTINGS["width"] and 0 <= y + dy < SETTINGS["height"]:
                            self.reveal_next(x + dx, y + dy, first=False)
                            self.contents[y + dy][x + dx].hidden = False
            

    def reveal_all(self, cell: Cell):
        cell.value = CLICKED_MINE
        self.state = LOSE
        if SETTINGS["play_sounds"]:
            threading.Thread(target=playsound, args=(
                SOUNDS + "game-over.mp3",)).start()

        for list in self.contents:
            for cell in list:
                if not cell.flagged:
                    cell.hidden = False
                elif cell.value != MINE:
                    cell.value = NOMINE
                    cell.flagged = False
                    cell.hidden = False

        return (cell.x_index, cell.y_index)
    
    
    def add_flags(self, x: int, y: int):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if 0 <= x + dx < SETTINGS["width"] and 0 <= y + dy < SETTINGS["height"]:
                    adj_cell: Cell = self.contents[y + dy][x + dx]
                    adj_cell.adj_flags += 1

    def remove_flags(self, x: int, y: int):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if 0 <= x + dx < SETTINGS["width"] and 0 <= y + dy < SETTINGS["height"]:
                    adj_cell: Cell = self.contents[y + dy][x + dx]
                    adj_cell.adj_flags -= 1

    def draw(self):
        for y in range(SETTINGS["height"]):
            for x in range(SETTINGS["width"]):
                self.contents[y][x].draw()
    
