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
from globals import (BG_COLOR, BLACK, CELL_EDGE, COOL, PAUSE_IS_PRESSED, DEAD, DISP,
                     DISP_H, DISP_W, FONT_SIZE, FONTS, GEAR, HOURGLASS, IMAGES, LOSE,
                     LRB_BORDER, MINE, PAUSE_FONT_SIZE, PAUSED, PLAYING,
                     PAUSE_WAS_PRESSED, RESET, SETTING_BUTTON_PRESSED, SETTINGS, SHOCKED, SMILE,
                     TOP_BORDER)
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
        self.displayed_screen = Screen.MAIN
        self.timerEvent = threading.Event()
        self.timer_thread = threading.Thread(target=self.timer)
        self.start_button = Button(DISP_W // 2, TOP_BORDER * 2, "START")
        self.bot_button = Button(DISP_W // 2, TOP_BORDER * 2 + 127, "AUTO SOLVER")
        self.quit_button = Button(DISP_W // 2, TOP_BORDER * 2 + 255, "QUIT")
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
            while self.grid.enabled and self.grid.clicked_cell:
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

    def reveal(self, x: int, y: int):
        """This method reveals the cell at the given coordinates if possible.

        Args:
            x (int): The x coordinate of the cell.
            y (int): The y coordinate of the cell.
        """
        if not self.grid.clicked_cell and SETTINGS["easy_start"]:
            self.grid.easy_start(x, y)

        self.grid.clicked_cell = self.grid.contents[y][x]
        mine_loc = self.grid.reveal_next(x, y)
        if mine_loc:
            self.reset_btn.value = DEAD
            self.grid.enabled = False
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

    def solve(self):
        pass # TODO


# ----------------------Event-Handlers---------------------- #
 # Cursor Events:

    def find_affected_cell(self, event: pygame.event.Event):
        """Reacts to player left click

        Args:
            game (Minesweeper.Game): The game to react to.
            event (pygame.event.Event, optional): The event associated with the left click.
        """
        global SETTING_BUTTON_PRESSED, RESET


        RESET = self.reset_btn.value
        match (self.displayed_screen):
            case Screen.MAIN:
                if not self.start_button.clicked and self.start_button.collidepoint(event.pos):
                    self.displayed_screen = Screen.GAME
                    self.grid.enabled = True
                    self.start_button.clicked = True
                else:
                    self.start_button.clicked = False
                    if not self.quit_button.clicked and self.quit_button.collidepoint(event.pos):
                        self.running = False
                        self.quit_button.clicked = True
                    else:
                        self.quit_button.clicked = False
                        if not self.bot_button.clicked and self.bot_button.collidepoint(event.pos):
                            self.displayed_screen = Screen.GAME
                            self.bot_button.clicked = True
                            self.solve()


            case Screen.GAME:
                x = (event.pos[0] - LRB_BORDER) / CELL_EDGE
                y = (event.pos[1] - TOP_BORDER) / CELL_EDGE
                if self.grid.enabled and TOP_BORDER < event.pos[1] < DISP_H - LRB_BORDER and LRB_BORDER < event.pos[0] < DISP_W - LRB_BORDER:
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
                        SETTING_BUTTON_PRESSED = True
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
                        SETTING_BUTTON_PRESSED = True


#-----#

    def highlight_cell(self, event: pygame.event.Event):
        """Reacts to cursor movement

        Args:
            game (Minesweeper.Game): The game to react in.
            event (pygame.event.Event): The event associated with the left click.
        """
        global RESET

        
        RESET = self.reset_btn.value
        if self.reset_btn.collidepoint(event.pos[0], event.pos[1]):
            RESET = SHOCKED

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
        DISP.blit(SPRITES[RESET], self.reset_btn)
        self.settings_btn.draw()

#-----#

    def draw_main(self):

        DISP.fill(BG_COLOR)
        match (self.displayed_screen):
            case Screen.MAIN:
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
        self.bot_button.draw()
        self.quit_button.draw()




# --------------------------------------------- #
  # Game Events:

    def pause_handler(self):

        global PAUSE_IS_PRESSED, PAUSE_WAS_PRESSED, SETTING_BUTTON_PRESSED

        keys = pygame.key.get_pressed()
        if RESET == SMILE and self.displayed_screen != Screen.MAIN:
            if keys[pygame.K_ESCAPE] or SETTING_BUTTON_PRESSED:
                if PAUSE_IS_PRESSED:
                    PAUSE_WAS_PRESSED = True
                PAUSE_IS_PRESSED = True
            else:
                PAUSE_WAS_PRESSED = False
                PAUSE_IS_PRESSED = False

            if PAUSE_IS_PRESSED and not PAUSE_WAS_PRESSED:
                self.grid.enabled = not self.grid.enabled
                if self.displayed_screen == Screen.GAME:
                    if SETTING_BUTTON_PRESSED:
                        self.displayed_screen = Screen.SETTINGS
                    else:
                        self.displayed_screen = Screen.PAUSE
                if self.timerEvent.is_set():
                    self.timerEvent.clear()
                elif keys[pygame.K_ESCAPE] and self.displayed_screen == Screen.PAUSE:
                    self.timerEvent.set()
                    self.displayed_screen = Screen.GAME
                elif SETTING_BUTTON_PRESSED and self.displayed_screen == Screen.SETTINGS:
                    self.timerEvent.set()
                    self.displayed_screen = Screen.GAME
                    self.save_settings()
        elif keys[pygame.K_ESCAPE] and RESET == SHOCKED:
            print("LOL")

        SETTING_BUTTON_PRESSED = False


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
            self.reset_btn.value = COOL
            self.grid.enabled = False
            for list in self.grid.contents:
                for cell in list:
                    if cell.value != MINE:
                        cell.hidden = False

#-----#

    def event_handler(self):
        
        global RESET

        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONDOWN:
                    self.find_affected_cell(event)
                case pygame.MOUSEMOTION:
                    if self.timerEvent.is_set():
                        self.highlight_cell(event)
                case pygame.KEYDOWN:
                    if self.displayed_screen == Screen.SETTINGS:
                        for box in self.textboxes:
                            box.text_handler(event.key, event.unicode)
                case pygame.QUIT:
                    self.running = False

        pygame.display.update()

#-----#

    def reset(self):
        """Resets the Game
        """
        self.reset_btn.value = SMILE
        self.elapsed_time = 0
        self.flagged_cells = 0
        self.grid.clicked_cell = None
        self.grid.troll_mode = False
        self.grid = Grid()
        self.grid.enabled = True

# ----------------------- #

    def run(self):
        """Starts the game threads & game loop
        """
        self.running = True
        if not self.timer_thread.is_alive():
            self.timer_thread.start()
            self.timerEvent.set()

        # fps = 0
        # temp = self.elapsed_time
        while self.running:
            self.event_handler()
            self.draw_main()
            self.pause_handler()
            # fps += 1
            # if temp != self.elapsed_time:
            #     temp = self.elapsed_time
            #     print(fps)
            #     fps = 0

        pygame.quit()


