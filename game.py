import json
import sys
import threading
import time
from math import floor
from typing import List

import pygame
from playsound import playsound

from cell import Cell
from client import Client
from globals import (BG_COLOR, BLACK, CELL_EDGE, COOL, CURRENT, DEAD, DISP,
                     DISP_H, DISP_W, FONT_SIZE, GEAR, HOST, LOSE, LRB_BORDER,
                     MINE, PATH, PAUSE_FONT_SIZE, PAUSED, PLAYING, PORT,
                     PREVIOUS, RESET, SET, SETTING, SETTINGS, SHOCKED, SMILE,
                     TOP_BORDER, WIN, HOURGLASS)
from grid import Grid
from sprites import SPRITES
from textbox import Textbox

pygame.init()

class Game(Client):

    clicked_cell: Cell = None
    setting_names: List[str] = ["Width", "Height", "Mines%", "Scale"]

    def __init__(self) -> None:
        super().__init__()
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
        self.text_boxes = [Textbox(TOP_BORDER * 1.3 + (Textbox.box_height + 20) * i) for i in range(4)]
        for i, name in enumerate(Game.setting_names):
            self.text_boxes[i].populate_box(name)
        self.grid = Grid()

    def timer(self):
        while self.running:
            while self.grid.contents_created and self.grid.state == PLAYING:
                self.timerEvent.wait()
                self.elapsed_time += 1
                time.sleep(1)

    def save_settings(self):
        """Tries to save the user altered settings

        Returns:
            int: 0 for no changes were made, 1 for changed successfully, 2 for error
        """
        error = False
        changed = False
        for box in self.text_boxes:
            setting = box.name.lower()
            setting_type = type(SETTINGS[setting])
            try:
                new_setting = setting_type(box.text)
            except:
                box.text = "ERR"
                error = True
            if new_setting != SETTINGS[setting]:
                SETTINGS[setting] = new_setting
                changed = True
        
        if error:
            return
        if changed:
            super().set_settings()
            self.running = False
            return
        self.timerEvent.set()
        self.grid.state = PLAYING


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

        elif self.grid.state in (PLAYING, SET) and self.settings_btn.hitbox.collidepoint(event.pos[0], event.pos[1]):
            if self.grid.troll_mode:
                self.grid.troll()
                for y in range(SETTINGS["height"]):
                    for x in range(SETTINGS["width"]):
                        self.grid.contents[y][x].hidden = False
            else:
                SETTING = True

        elif self.grid.state == SET:
            for box in self.text_boxes:
                if box.rect.collidepoint(event.pos):
                    box.active = True
                else:
                    box.active = False
        elif self.grid.state in (PLAYING, WIN, LOSE) and self.reset_btn.hitbox.collidepoint(event.pos[0], event.pos[1]):
            if self.grid.troll_mode:
                SETTINGS["mines%"] = 15
                super().set_settings()
                sys.exit() # TODO
            else:
                self.reset()

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
        DISP.blits([(SPRITES[MINE], (LRB_BORDER, LRB_BORDER)),
                     (mines_left, mines_left.get_rect(center=(LRB_BORDER + CELL_EDGE * 1.6, LRB_BORDER + CELL_EDGE / 1.75))),
                      (SPRITES[HOURGLASS], (LRB_BORDER, LRB_BORDER + CELL_EDGE)),
                       (time_elapsed, time_elapsed.get_rect(center=(LRB_BORDER + CELL_EDGE * 1.6, LRB_BORDER + CELL_EDGE * 1.6)))])

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
                    center=(DISP_W // 2, TOP_BORDER + SETTINGS["scale"] * 10)))
            for box in self.text_boxes:
                text = box.font.render(box.name, 0, BLACK)
                DISP.blit(text, (LRB_BORDER, box.rect.top))
                box.draw()
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
            if self.grid.state == PLAYING:
                if SETTING:
                    self.grid.state = SET
                else:
                    self.grid.state = PAUSED
            if self.timerEvent.is_set():
                self.timerEvent.clear()
            elif keys[pygame.K_ESCAPE] and self.grid.state == PAUSED:
                    self.timerEvent.set()
                    self.grid.state = PLAYING
            elif SETTING and self.grid.state == SET:
                self.save_settings()
    
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
                case pygame.KEYDOWN:
                    if self.grid.state == SET:
                        for box in self.text_boxes:
                            box.text_handler(event.key, event.unicode)
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
            self.event_handler()
            self.draw_panel()
            self.draw_main()
            self.pause_handler()

        pygame.quit()