import threading
from math import floor
import time

import pygame

from cell import Cell
from grid import Grid
from globals import (BG_COLOR, CELL_EDGE, COOL, HOST, LOSE, MINE, PAUSE_FONT_SIZE, PAUSED, PLAYING, GEAR, DISP, DISP_H, DISP_W, LRB_BORDER, PATH, PORT,
                     RESET, SET, SETTINGS, DEAD, SHOCKED, SMILE, TOP_BORDER, WIN, BLACK, FONT_SIZE, CURRENT, PREVIOUS, SETTING)
from sprites import SPRITES, HOURGLASS, MINESPR
pygame.init()


class Game():

    clicked_cell: Cell = None

    def __init__(self) -> None:
        self.running = True
        self.elapsed_time = 0
        self.flagged_cells = 0
        self.timerEvent = threading.Event()
        self.timer_thread = threading.Thread(target=self.timer)
        self.font = pygame.font.Font(
            PATH + "Font.ttf", FONT_SIZE)
        self.pause_font = pygame.font.Font(
            PATH + "Font.ttf", PAUSE_FONT_SIZE)
        self.settings_btn = Cell(
            SETTINGS["width"] - 0.75, -2.75, value=GEAR, hidden=False, create_hitbox=True)
        self.reset_btn = Cell(
            SETTINGS["width"] / 2 - 0.5, -2, value=RESET, hidden=False, create_hitbox=True)
        self.settings_btn.create_hitbox()
        self.reset_btn.create_hitbox()
        self.grid = Grid()

    def timer(self):
        while self.running:
            while self.grid.contents_created and self.grid.state == PLAYING:
                self.timerEvent.wait()
                self.elapsed_time += 1
                time.sleep(1)


    def reveal(self, x: int, y: int):
        """This method reveals the cell at the given coordinates if possible.

        Args:
            x (int): The x coordinate of the cell.
            y (int): The y coordinate of the cell.
        """
        if not self.grid.contents_created:
            self.grid.create_layout(x, y)

        self.grid.clicked_cell = self.grid.contents[y][x]
        mine_loc = self.grid.reveal_next(x, y)
        if mine_loc:
            self.reset_btn.value = DEAD
            return mine_loc

    def flag(self, x: int, y: int):
        """This method Flags/Unflags the cell at the given coordinates.

        Args:
            x (int): The x coordinate of the cell to flag.
            y (int): The y coordinate of the cell to
        """
        if self.grid.contents[y][x].hidden:
            if self.grid.contents[y][x].flagged:
                self.grid.contents[y][x].flagged = False
                self.flagged_cells -= 1
            else:
                self.grid.contents[y][x].flagged = True
                self.flagged_cells += 1

        if self.flagged_cells == self.grid.mines:
            self.endgame_handler()

# ----------------------Event-Handlers---------------------- #
 # Cursor Events:

    def find_affected_cell(self, event: pygame.event.Event):
        """Reacts to player left click

        Args:
            game (Minesweeper.Game): The game to react to.
            event (pygame.event.Event, optional): The event associated with the left click.
        """

        global SETTING

        x = (event.pos[0] - LRB_BORDER) / CELL_EDGE
        y = (event.pos[1] - TOP_BORDER) / CELL_EDGE
        if self.grid.state == PLAYING and TOP_BORDER < event.pos[1] < DISP_H - LRB_BORDER and LRB_BORDER < event.pos[0] < DISP_W - LRB_BORDER:
            x = floor(x)
            y = floor(y)
            actions = {
                1: self.reveal,
                3: self.flag,
            }
            try:
                actions[event.button](x, y)
            except:
                pass

        elif self.grid.state == PLAYING and self.reset_btn.hitbox.collidepoint(event.pos[0], event.pos[1]):
            self.reset()
        elif self.settings_btn.hitbox.collidepoint(event.pos[0], event.pos[1]):
            SETTING = True
            if self.grid.troll_mode:
                if self.grid.contents[0][0].hidden == False:
                    self.grid.troll()
                else:
                    for y in range(SETTINGS["height"]):
                        for x in range(SETTINGS["width"]):
                            self.grid.contents[y][x].hidden = False

        elif self.settings_btn.hitbox.collidepoint(event.pos[0], event.pos[1]) and self.grid.troll_mode:
            if self.grid.contents[0][0].hidden == False:
                self.grid.troll()
            else:
                for y in range(SETTINGS["height"]):
                    for x in range(SETTINGS["width"]):
                        self.grid.contents[y][x].hidden = False

#-----#
  
    def highlight_cell(self, event: pygame.event.Event):
        """Reacts to cursor movement

        Args:
            game (Minesweeper.Game): The game to react in.
            event (pygame.event.Event): The event associated with the left click.
        """
        if self.reset_btn.hitbox.collidepoint(event.pos[0], event.pos[1]):
            self.reset_btn.value = SHOCKED
        elif self.grid.state == LOSE:
            self.reset_btn.value = DEAD
        elif self.reset_btn.value != RESET:
            self.reset_btn.value = RESET

# --------------------------------------------- #
 # Draw events:

    def draw_panel(self):
        mines_left = self.font.render(
            str(self.grid.mines - self.flagged_cells), 0, BLACK)
        time_elapsed = self.font.render(str(self.elapsed_time), 0, BLACK)
        DISP.fill(BG_COLOR)
        DISP.blits([(MINESPR, (LRB_BORDER, LRB_BORDER)), (mines_left, (LRB_BORDER + 15, LRB_BORDER + 5)), (HOURGLASS, (LRB_BORDER,
                    LRB_BORDER * 2)), (time_elapsed, (LRB_BORDER + 15, LRB_BORDER * 2 + 5))])

        self.settings_btn.draw()
        self.reset_btn.draw()

#-----#

    def draw_main(self):
        if self.timerEvent.is_set():
            for y in range(SETTINGS["height"]):
                for x in range(SETTINGS["width"]):
                    self.grid.contents[y][x].draw()
        elif self.grid.state == SET:
            text = self.pause_font.render("SETTINGS", 0, BLACK)
            DISP.blit(text, text.get_rect(
                    center=(DISP_W // 2, TOP_BORDER)))
        else:
            text = self.pause_font.render("PAUSED", 0, BLACK)
            DISP.blit(text, text.get_rect(
                center=(DISP_W // 2, DISP_H // 2)))

        if self.grid.state == WIN or self.grid.state == LOSE:
            DISP.blit(SPRITES[self.grid.state], (LRB_BORDER, TOP_BORDER))

# --------------------------------------------- #
  # Game Events:

    def pause_handler(self):

        global CURRENT, PREVIOUS, SETTING

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or SETTING:
            if CURRENT:
                PREVIOUS = True
            CURRENT = True
        else:
            PREVIOUS = False
            CURRENT = False

        if CURRENT and not PREVIOUS:
            if SETTING:
                self.grid.state = SET
            else:
                self.grid.state = PAUSED
            if self.timerEvent.is_set():
                self.timerEvent.clear()
            else:
                self.timerEvent.set()
                self.grid.state = PLAYING
    
        SETTING = False


#-----#

    def endgame_handler(self):
        
        global RESET

        b = False
        for list in self.grid.contents:
            for cell in list:
                if cell.value == MINE and not cell.flagged:
                    b = True
                    break

            if b:
                break

        else:
            RESET = COOL
            self.reset_btn.value = COOL
            for list in self.grid.contents:
                for cell in list:
                    if cell.value != -1:
                        cell.hidden = False
            self.grid.state = WIN

#-----#

    def event_handler(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONDOWN:
                    self.find_affected_cell(event)
                case pygame.MOUSEMOTION:
                    if self.timerEvent.is_set():
                        self.highlight_cell(event)
                case pygame.QUIT:
                    self.running = False

        pygame.display.update()

#-----#

    def reset(self):
        """Resets the Game
        """
        global RESET

        RESET = SMILE
        self.elapsed_time = 0
        self.flagged_cells = 0
        self.grid.contents_created = False
        self.grid.troll_mode = False
        self.grid = Grid()


# ----------------------- #
  
    def run(self):
        """Starts the game threads & game loop
        """
        self.running = True
        if not self.timer_thread.is_alive():
            self.timer_thread.start()
            self.timerEvent.set()

        self.play()

# ----------------------- #
    
    def play(self):
        """This function has the main game loop and occupies the drawThread of the game.
        """
        global RESET

        while self.running:
            print(self.grid.state)
            self.event_handler()
            self.draw_panel()
            self.draw_main()
            self.pause_handler()

        pygame.quit()