"""Simulation of the forest fire percolation model"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UITextEntryLine, UIButton

from base_percolation import BasePercolation

ALLOWED_CHARS = [str(i) for i in range(11)] + [".", "e", "E", "+", "-"]

GROUND = (44, 20, 1)
TREE = (0, 100, 0)
FIRE = (255, 40, 7)


class ForestFire(BasePercolation):
    """Class to handle forest fire percolation."""

    def __init__(self):
        super().__init__(name="Fire Percolation", grid_size=180)
        self.timer = 0
        self.is_playing = False
        self.draw_surface = pygame.Surface((self.grid_size, self.grid_size))
        self.font = pygame.font.SysFont(None, 25)

        self.tree_fraction_entry = None
        self.tree_fraction_label = None
        self.prob_grow_entry = None
        self.prob_grow_entry_label = None
        self.prob_fire_entry = None
        self.prob_fire_label = None
        self.button_play = None

    def enable(self, gui_manager):
        # Text entry box for initial tree coverage fraction
        self.tree_fraction_entry = UITextEntryLine(
            pygame.Rect((350, 670), (100, 20)), gui_manager
        )
        self.tree_fraction_entry.allowed_characters = ALLOWED_CHARS
        self.tree_fraction_entry.set_text("0.2")
        self.tree_fraction_label = UILabel(
            pygame.Rect((10, 670), (300, 20)),
            "Initial tree coverage fraction: ",
            gui_manager,
        )

        # Text entry box for probability of tree growth
        self.prob_grow_entry = UITextEntryLine(
            pygame.Rect((350, 710), (100, 20)), gui_manager
        )
        self.prob_grow_entry.allowed_characters = ALLOWED_CHARS
        self.prob_grow_entry.set_text("0.01")
        self.prob_grow_entry_label = UILabel(
            pygame.Rect((10, 710), (300, 20)), "Growth probability: ", gui_manager
        )

        # Text entry box for probability of spontaneous tree fire
        self.prob_fire_entry = UITextEntryLine(
            pygame.Rect((350, 750), (100, 20)), gui_manager
        )
        self.prob_fire_entry.allowed_characters = ALLOWED_CHARS
        self.prob_fire_entry.set_text("0.0001")
        self.prob_fire_label = UILabel(
            pygame.Rect((10, 750), (300, 20)),
            "Spontaneous fire probability: ",
            gui_manager,
        )

        self.button_play = UIButton(pygame.Rect(620, 120, 90, 50), "Play", gui_manager)
        self.generate_random_start()

    def draw(self, window_surf: pygame.Surface):
        """Draws trees/fires using treegrid and firegrid"""
        if self.draw_call:
            self.draw_surface.fill(GROUND)
            for i in range(self.grid.size):
                row = i // self.grid_size
                column = i % self.grid_size

                if self.grid[i] == 1:
                    self.draw_surface.set_at((column, row), TREE)
                elif self.grid[i] == 2:
                    self.draw_surface.set_at((column, row), FIRE)

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

    def validate_entries(self) -> bool:
        """Check that the entries have valid float values"""
        try:
            float(self.tree_fraction_entry.get_text())
            float(self.prob_fire_entry.get_text())
            float(self.prob_grow_entry.get_text())
            self.generate_random_start()
            return True
        except ValueError:
            return False

    def process_events(self, event: pygame.event.Event):
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button_play and self.validate_entries():
                self.is_playing = not self.is_playing
                if self.is_playing:
                    self.button_play.set_text("Pause")
                else:
                    self.button_play.set_text("Play")
        elif event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            self.is_playing = False
            self.button_play.set_text("Play")
            if self.validate_entries():
                self.generate_random_start()

    def reset_outer_edges(self):
        """Resets the outer edges of the grid to zero"""
        self.grid[0 : self.grid_size] = 0
        self.grid[self.grid.size - self.grid_size :] = 0
        self.grid[0 :: self.grid_size] = 0
        self.grid[self.grid_size - 1 :: self.grid_size] = 0

    def generate_random_start(self):
        """Generate initial tree distribution"""
        # Resets array
        self.grid = np.zeros_like(self.grid)
        # Places random trees randomly in array
        tree_fraction = float(self.tree_fraction_entry.get_text())
        self.grid = (np.random.rand(self.grid.size) < tree_fraction).astype(np.int)

        # Outer edges of grid set to be empty - this simplifies
        # fire spread code (see Burning)
        self.reset_outer_edges()

        self.draw_call = True

    def step(self):
        """Grow trees, set fires and allow them to spread"""
        prob_grow = float(self.prob_grow_entry.get_text())
        prob_fire = float(self.prob_fire_entry.get_text())

        # Look through every point in grid
        for i in range(self.grid.size - self.grid_size - 1):
            # Extract the point and the eight points that surround it
            point = self.grid[i]
            north = self.grid[i - self.grid_size]
            north_east = self.grid[i - self.grid_size + 1]
            east = self.grid[i + 1]
            south_east = self.grid[i + self.grid_size + 1]
            south = self.grid[i + self.grid_size]
            south_west = self.grid[i + self.grid_size - 1]
            west = self.grid[i - 1]
            north_west = self.grid[i - self.grid_size - 1]
            # Spontaneous growth
            if point == 0 and np.random.random() < prob_grow:
                # Grown tree is +1, -1 is used so it doesn't get checked later on
                self.grid[i] = -1

            # Spontaneous fire
            elif point == 1 and np.random.random() < prob_fire:
                # Fire is +2, -2 is used so it doesn't get checked later on
                self.grid[i] = -2

            # Fire spread
            elif point == 2:
                # Burns all surrounding tiles, sets them to -2 so that they're ignored
                self.grid[i - self.grid_size] = -2 if north else north
                self.grid[i - self.grid_size + 1] = -2 if north_east else north_east
                self.grid[i + 1] = -2 if east else east
                self.grid[i + self.grid_size + 1] = -2 if south_east else south_east
                self.grid[i + self.grid_size] = -2 if south else south
                self.grid[i + self.grid_size - 1] = -2 if south_west else south_west
                self.grid[i - 1] = -2 if west else west
                self.grid[i - self.grid_size - 1] = -2 if north_west else north_west

                # Original burning tree burns itself out
                self.grid[i] = 0

        # Flip ignored sites and clear edges to stop overflow error
        self.grid = np.absolute(self.grid)

        self.reset_outer_edges()

        self.draw_call = True
