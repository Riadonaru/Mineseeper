import sys
import threading
import time
from math import floor
from typing import List

import pygame
from button import Button

from cell import Cell
from checkbox import Checkbox
from client import Client
from globals import (BG_COLOR, BLACK, CELL_EDGE, COOL, CURRENT, DEAD, DISP,
                     DISP_H, DISP_W, FONT_SIZE, FONTS, GEAR, HOURGLASS, IMAGES, LOSE,
                     LRB_BORDER, MINE, PAUSE_FONT_SIZE, PAUSED, PLAYING,
                     PREVIOUS, RESET, SET, SETTING, SETTINGS, SHOCKED, SMILE,
                     TOP_BORDER, WIN)
from grid import Grid
from screens import Screen
from sprites import SPRITES
from textbox import Textbox

pygame.init()


class Game(Client):

    font = pygame.font.Font(FONTS + "Font.ttf", FONT_SIZE)
    pause_font = pygame.font.Font(FONTS + "Font.ttf", PAUSE_FONT_SIZE)

    def __init__(self) -> None:
        super().__init__()
        self.running = True
        self.elapsed_time = 0
        self.flagged_cells = 0
        self.displayed_screen = Screen.MENU
        self.timerEvent = threading.Event()
        self.timer_thread = threading.Thread(target=self.timer)
        self.start_button = Button(IMAGES + "start_btn.png")
        self.settings_btn = Cell(
            SETTINGS["width"] - 0.75, -2.75, value=GEAR, hidden=False)
        self.reset_btn = Cell(
            SETTINGS["width"] / 2 - 0.5, -2, value=RESET, hidden=False)
        self.textboxes: List[Textbox] = []
        self.checkboxes: List[Checkbox] = []
        for i, setting in enumerate(SETTINGS):
            setting_type = type(SETTINGS[setting])
            if setting_type is bool:
                self.checkboxes.append(Checkbox(setting, TOP_BORDER * 1.3 + (Textbox.box_height + 20) * i))
            else:
                self.textboxes.append(Textbox(setting, TOP_BORDER * 1.3 + (Textbox.box_height + 20) * i))
               
        self.grid = Grid()

    def timer(self):
        while self.running:
            while self.grid.clicked_cell != None and self.grid.state == PLAYING:
                self.timerEvent.wait()
                self.elapsed_time += 1
                time.sleep(1)

    def save_settings(self):
        """Tries to save the user altered settings
        """
        error = False
        changed = False
        for box in self.textboxes:
            setting = box.name.lower().replace(" ", "_")
            setting_type = type(SETTINGS[setting])
            if box.text != "":
                try:
                    new_setting = setting_type(box.text)
                    if new_setting != SETTINGS[setting]:
                        SETTINGS[setting] = new_setting
                        changed = True
                except:
                    box.text = "ERR"
                    error = True
            else:
                box.text = str(SETTINGS[setting])

        for box in self.checkboxes:
            setting = box.name.lower().replace(" ", "_")
            if not box.active == SETTINGS[setting]:
                SETTINGS[setting] = box.active
                changed = True

        if error:
            return
        if changed:
            super().set_settings()
            self.running = False
            return
        self.timerEvent.set()
        self.grid.state = PLAYING
        self.displayed_screen = Screen.GAME

    def reveal(self, x: int, y: int):
        """This method reveals the cell at the given coordinates if possible.

        Args:
            x (int): The x coordinate of the cell.
            y (int): The y coordinate of the cell.
        """
        if self.grid.clicked_cell == None and SETTINGS["easy_start"]:
            self.grid.easy_start(x, y)

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
                self.grid.remove_flags(x, y)
            else:
                self.grid.contents[y][x].flagged = True
                self.flagged_cells += 1
                self.grid.add_flags(x, y)

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



        match (self.displayed_screen):
            case Screen.MENU:
                if not self.start_button.clicked and self.start_button.collidepoint(event.pos):
                    self.displayed_screen = Screen.GAME
                    self.grid.state = PLAYING

            case Screen.GAME:
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

                elif self.settings_btn.collidepoint(event.pos[0], event.pos[1]):
                    if self.grid.troll_mode:
                        self.grid.troll()
                        for y in range(SETTINGS["height"]):
                            for x in range(SETTINGS["width"]):
                                self.grid.contents[y][x].hidden = False
                    else:
                        SETTING = True
                elif self.reset_btn.collidepoint(event.pos[0], event.pos[1]):
                    if self.grid.troll_mode:
                        SETTINGS["mines%"] = 15
                        super().set_settings()
                        self.running = False # TODO
                    else:
                        self.reset()

            case Screen.SETTINGS:
                for box in self.textboxes:
                    if box.collidepoint(event.pos):
                        box.active = True
                        box.text = ""
                    else:
                        box.active = False

                for box in self.checkboxes:
                    if box.collidepoint(event.pos):
                        box.active = not box.active

                if self.settings_btn.collidepoint(event.pos[0], event.pos[1]):
                    if self.grid.troll_mode:
                        self.grid.troll()
                        for y in range(SETTINGS["height"]):
                            for x in range(SETTINGS["width"]):
                                self.grid.contents[y][x].hidden = False
                    else:
                        SETTING = True


#-----#

    def highlight_cell(self, event: pygame.event.Event):
        """Reacts to cursor movement

        Args:
            game (Minesweeper.Game): The game to react in.
            event (pygame.event.Event): The event associated with the left click.
        """
        if self.reset_btn.collidepoint(event.pos[0], event.pos[1]):
            self.reset_btn.value = SHOCKED
        elif self.grid.state == LOSE:
            self.reset_btn.value = DEAD
        elif self.reset_btn.value != RESET:
            self.reset_btn.value = RESET

# --------------------------------------------- #
 # Draw events:

    def draw_panel(self):
        mines_left = Game.font.render(
            str(self.grid.mines - self.flagged_cells), 0, BLACK)
        time_elapsed = Game.font.render(str(self.elapsed_time), 0, BLACK)
        DISP.blits([(SPRITES[MINE], (LRB_BORDER, LRB_BORDER)),
                    (mines_left, mines_left.get_rect(
                        center=(LRB_BORDER + CELL_EDGE * 1.6, LRB_BORDER + CELL_EDGE / 1.75))),
                    (SPRITES[HOURGLASS], (LRB_BORDER, LRB_BORDER + CELL_EDGE)),
                    (time_elapsed, time_elapsed.get_rect(center=(LRB_BORDER + CELL_EDGE * 1.6, LRB_BORDER + CELL_EDGE * 1.6)))])

        self.settings_btn.draw()
        self.reset_btn.draw()

#-----#

    def draw_main(self):

        DISP.fill(BG_COLOR)
        match (self.displayed_screen):
            case Screen.MENU:
                self.draw_main_menu()
            case Screen.GAME:
                self.draw_panel()
                self.grid.draw()
            case Screen.SETTINGS:
                self.draw_panel()
                self.draw_settings()
            case Screen.PAUSE:
                self.draw_panel()
                self.draw_pause_menu()




#-----#

    def draw_settings(self):
        text = Game.pause_font.render("SETTINGS", 0, BLACK)
        DISP.blit(text, text.get_rect(
            center=(DISP_W // 2, TOP_BORDER + SETTINGS["scale"] * 10)))
        for box in self.textboxes:
            box.draw()
        
        for box in self.checkboxes:
            box.draw()
 

#-----#

    def draw_pause_menu(self):
        text = Game.pause_font.render("PAUSED", 0, BLACK)
        DISP.blit(text, text.get_rect(
            center=(DISP_W // 2, DISP_H // 2)))
        

    def draw_main_menu(self):
        self.start_button.draw()




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
                    self.displayed_screen = Screen.SETTINGS
                else:
                    self.grid.state = PAUSED
                    self.displayed_screen = Screen.PAUSE
            if self.timerEvent.is_set():
                self.timerEvent.clear()
            elif keys[pygame.K_ESCAPE] and self.grid.state == PAUSED:
                self.timerEvent.set()
                self.grid.state = PLAYING
                self.displayed_screen = Screen.GAME
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
                    if cell.value != MINE:
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
                        for box in self.textboxes:
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
        self.grid.clicked_cell = None
        self.grid.troll_mode = False
        self.grid = Grid()
        self.grid.state = PLAYING


# ----------------------- #

    def run(self):
        """Starts the game threads & game loop
        """
        self.running = True
        if not self.timer_thread.is_alive():
            self.timer_thread.start()
            self.timerEvent.set()

        while self.running:
            self.event_handler()
            self.draw_main()
            self.pause_handler()

        pygame.quit()


