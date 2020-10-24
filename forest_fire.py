"""Simulation of the forest fire percolation model"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui

from base_percolation import BasePercolation


class ForestFire(BasePercolation):
    """Class to handle forest fire percolation."""

    def __init__(self):
        super().__init__(name="Fire Percolation", grid_size=180)
        self.timer = 0
        self.is_playing = False
        self.draw_surface = pygame.Surface(self.grid_size)
        self.font = pygame.font.SysFont(None, 25)

        self.initial_textentry = None
        self.initial_textentry_label = None
        self.p_grow_textentry = None
        self.p_grow_textentry_label = None
        self.p_fire_textentry = None
        self.p_fire_textentry_label = None
        self.button_play = None

    def enable(self, gui_manager):
        # Text entry box for initial tree coverage fraction
        self.initial_textentry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((350, 670), (100, 20)), gui_manager
        )
        self.initial_textentry.allowed_characters = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            ".",
        ]
        self.initial_textentry.set_text("0.2")
        self.initial_textentry_label = pygame_gui.elements.UILabel(
            pygame.Rect((10, 670), (300, 20)),
            "Initial tree coverage fraction: ",
            gui_manager,
        )

        # Text entry box for probability of tree growth
        self.p_grow_textentry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((350, 710), (100, 20)), gui_manager
        )
        self.initial_textentry.allowed_characters = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            ".",
        ]
        self.p_grow_textentry.set_text("0.01")
        self.p_grow_textentry_label = pygame_gui.elements.UILabel(
            pygame.Rect((10, 710), (300, 20)), "Growth probability: ", gui_manager
        )

        # Text entry box for probability of spontaneous tree fire
        self.p_fire_textentry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((350, 750), (100, 20)), gui_manager
        )
        self.initial_textentry.allowed_characters = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            ".",
        ]
        self.p_fire_textentry.set_text("0.0001")
        self.p_fire_textentry_label = pygame_gui.elements.UILabel(
            pygame.Rect((10, 750), (300, 20)),
            "Spontaneous fire probability: ",
            gui_manager,
        )

        self.button_play = pygame_gui.elements.UIButton(
            pygame.Rect(620, 120, 90, 50), "Play", gui_manager
        )
        self.generate_random_start()

    def draw(self, window_surf: pygame.Surface):
        """Draws trees/fires using treegrid and firegrid"""
        if self.draw_call:
            self.draw_surface.fill((44, 20, 1))
            for index in range(self.grid.size):
                if self.grid[index] == 1:
                    self.draw_surface.set_at(
                        (index % self.grid_width, index // self.grid_width), (0, 100, 0)
                    )
                elif self.grid[index] == 2:
                    self.draw_surface.set_at(
                        (index % self.grid_width, index // self.grid_width),
                        (255, 40, 7),
                    )

            self.draw_call = False
        window_surf.blit(
            pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60)
        )

    def update(self, delta):
        self.timer += delta
        if self.timer > 0.1:
            self.timer -= 0.1
            if self.is_playing:
                self.step()

    def process_events(self, event: pygame.event.Event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.button_play:
                    self.is_playing = not self.is_playing
                    if self.is_playing:
                        self.button_play.set_text("Pause")
                    else:
                        self.button_play.set_text("Play")
            elif event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                self.is_playing = False
                self.button_play.set_text("Play")
                ci = self.initial_textentry.get_text().count(".")
                cf = self.p_fire_textentry.get_text().count(".")
                cg = self.p_grow_textentry.get_text().count(".")
                if (ci + cg + cf) == 3:
                    self.generate_random_start()

    def generate_random_start(self):
        """Generate initial tree distribution"""
        # Resets array
        self.grid = np.zeros_like(self.grid)
        #  Places random trees randomly in array
        self.grid = (
            np.random.rand(self.grid.size) < float(self.initial_textentry.get_text())
        ).astype(np.int)

        # Outer edges of treegrid_array set to be empty - this simplifies
        # fire spread code (see Burning)
        self.grid[0 : self.grid_width] = 0
        self.grid[self.grid.size - self.grid_width :] = 0
        self.grid[0 :: self.grid_width] = 0
        self.grid[self.grid_width - 1 :: self.grid_width] = 0
        self.draw_call = True

    def step(self):
        """Grow trees, set fires and allow them to spread"""
        # Look through every point in grid
        for index in range(self.grid.size - self.grid_width - 1):
            # Spontaneous growth
            if self.grid[index] == 0 and np.random.random() < float(
                self.p_grow_textentry.get_text()
            ):
                # Grown tree is +1, -1 is used so it doesn't get checked later on
                self.grid[index] = -1
            # Spontaneous fire
            elif self.grid[index] == 1 and np.random.random() < float(
                self.p_fire_textentry.get_text()
            ):
                # Fire is +2, -2 is used so it doesn't get checked later on
                self.grid[index] = -2
            # Fire spread
            elif self.grid[index] == 2:
                # Burns all surrounding tiles, sets them to -2 so that they're ignored
                self.grid[index - 1] = (
                    -2 if self.grid[index - 1] else self.grid[index - 1]
                )
                self.grid[index + 1] = (
                    -2 if self.grid[index + 1] else self.grid[index + 1]
                )
                self.grid[index - self.grid_width] = (
                    -2
                    if self.grid[index - self.grid_width]
                    else self.grid[index - self.grid_width]
                )
                self.grid[index + self.grid_width] = (
                    -2
                    if self.grid[index + self.grid_width]
                    else self.grid[index + self.grid_width]
                )
                self.grid[index - self.grid_width - 1] = (
                    -2
                    if self.grid[index - self.grid_width - 1]
                    else self.grid[index - self.grid_width - 1]
                )
                self.grid[index - self.grid_width + 1] = (
                    -2
                    if self.grid[index - self.grid_width + 1]
                    else self.grid[index - self.grid_width + 1]
                )
                self.grid[index + self.grid_width - 1] = (
                    -2
                    if self.grid[index + self.grid_width - 1]
                    else self.grid[index + self.grid_width - 1]
                )
                self.grid[index + self.grid_width + 1] = (
                    -2
                    if self.grid[index + self.grid_width + 1]
                    else self.grid[index + self.grid_width + 1]
                )

                # Original burning tree burns itself out
                self.grid[index] = 0

        # Flip ignored sites and clear edges to stop overflow error
        self.grid = np.absolute(self.grid)

        self.grid[0 : self.grid_width] = 0
        self.grid[self.grid.size - self.grid_width :] = 0
        self.grid[0 :: self.grid_width] = 0
        self.grid[self.grid_width - 1 :: self.grid_width] = 0

        self.draw_call = True
