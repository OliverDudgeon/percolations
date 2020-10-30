"""Simulation of a 2D square site lattice percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import time

import numpy as np
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIHorizontalSlider
import matplotlib.pyplot as plt
from multiprocessing import Pool
from scipy.ndimage import measurements

from base_percolation import BasePercolation

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BTN_WH = (90, 50)

GRID_CONTAINER_SIZE = 600
GRID_SIZE = 10


class SitePercolation(BasePercolation):
    """Class to handle percolation things."""

    def __init__(self):
        super().__init__(name="Site Percolation", grid_size=GRID_SIZE)

        self.cluster = np.zeros_like(self.grid, dtype=np.int)  # Init cluster values
        self.draw_call = False  # Used to optimize draw calls
        self.draw_clusters = False  # Used to draw clusters
        self.labels = np.zeros(
            self.grid.size // 2, dtype=np.int
        )  # Used for labeling clusters

        # Create surface to draw onto, for optimisation
        self.draw_surface = pygame.Surface((self.grid_size, self.grid_size))
        self.font = pygame.font.SysFont(None, 25)  # Init font for drawing

        self.p_slider = None
        self.button_step = None
        self.button_path = None
        self.button_graph = None

    def step(self):
        """Do one step of the simulation"""
        self.cluster = np.zeros_like(self.grid, dtype=np.int)  # Reset cluster values

        # Repopulate sites
        self.grid = (
            np.random.rand(self.grid.size) < self.p_slider.current_value
        ).astype(np.int)
        self.draw_call = True  # Call a redraw
        self.draw_clusters = False

    def enable(self, gui_manager: pygame_gui.UIManager):
        """Create the UI elements"""
        self.p_slider = UIHorizontalSlider(
            pygame.Rect((10, 670), (600, 20)),
            0.25,
            (0.0, 1.0),
            gui_manager,
        )
        self.button_step = UIButton(pygame.Rect(620, 60, *BTN_WH), "Step", gui_manager)
        self.button_path = UIButton(
            pygame.Rect(620, 120, *BTN_WH), "Cluster", gui_manager
        )
        self.button_graph = UIButton(
            pygame.Rect(620, 180, *BTN_WH), "Plot", gui_manager
        )

        self.step()  # Initial draw

    def draw(self, window_surf) -> None:
        surface = self.draw_surface
        if self.draw_call:  # Only redraw grid if it has changed
            # Clear old grid by making every cell white
            surface.fill(WHITE)

            #  Loop through all active sites and fill pixel black
            for i in range(self.grid.size):
                row = i % self.grid_size
                column = i // self.grid_size
                if self.grid[i] == 1:
                    self.draw_surface.set_at((row, column), BLACK)
            self.draw_call = False  # No need to redraw now

        # Copy surface to main window
        window_surf.blit(
            pygame.transform.scale(
                self.draw_surface, (GRID_CONTAINER_SIZE, GRID_CONTAINER_SIZE)
            ),
            (10, 60),
        )
        # Copy surface to main window
        window_surf.blit(
            pygame.transform.scale(surface, (GRID_CONTAINER_SIZE, GRID_CONTAINER_SIZE)),
            (10, 60),
        )

        if self.draw_clusters:
            site_size = GRID_CONTAINER_SIZE // self.grid_size
            for i in range(self.grid.size):
                row = i % self.grid_size
                column = i // self.grid_size
                if not self.cluster[i]:
                    continue
                img = self.font.render(str(self.cluster[i]), True, RED, None)
                cluster = (10 + row * site_size, 60 + column * site_size)
                scaled = pygame.transform.smoothscale(img, (site_size, site_size))
                window_surf.blit(scaled, cluster)

                # Transform index of 1D array to 2D array
                pos = (i % self.grid_size, i // self.grid_size)
                surface.set_at(pos, BLACK)

        # Draw the value of the probability slider
        text = f"p: {self.p_slider.current_value:.3f}"
        img = self.font.render(text, True, WHITE, None)
        window_surf.blit(img, (300 - img.get_rect().width // 2, 690))

    def process_events(self, event: pygame.event.Event):
        # Handle pygame_gui button events
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button_step:
                self.step()
            elif event.ui_element == self.button_path:
                self.hoshen_kopelman()
                self.draw_clusters = True
            elif event.ui_element == self.button_graph:
                self.simulate()

    def update(self, delta) -> None:
        return

    def _find(self, old_label):
        """Loops through labels indexing them correctly"""
        new_label = old_label
        while (self.labels[new_label] != new_label).any():
            new_label = self.labels[new_label]

        while (self.labels[old_label] != old_label).any():
            label = self.labels[old_label]
            self.labels[old_label] = new_label
            old_label = label
        return new_label

    def _union(self, label1, label2):
        """Links to cluster together"""
        label = self._find(label2)
        self.labels[self._find(label1)] = label
        return label

    def hoshen_kopelman(self):
        self.cluster, _ = measurements.label(
            self.grid.reshape((self.grid_size, self.grid_size))
        )
        self.cluster = self.cluster.reshape(self.grid.size)
        # """
        # Implementation of the Hoshen-Kopelman clustering algorithm
        # returns the number of clusters found
        # """
        # # Array of sites and what cluster they're in
        # self.cluster = self.grid.astype(np.int)
        # # Links clusters together that we're not previously found to be together
        # self.labels[:] = 0

        # for i in range(self.grid.size):
        #     row = i % self.grid_size
        #     column = i // self.grid_size
        #     if self.grid[i]:  # Loops through all the active sites
        #         # Cluster number of left site
        #         top = 0 if row == 0 else self.cluster[i - 1]
        #         # Cluster number of top site
        #         left = 0 if column == 0 else self.cluster[i - self.grid_size]
        #         # Counts how many sites are next to it
        #         cluster = int(top > 0) + int(left > 0)
        #         if cluster == 0:  # If not in cluster, add to new one
        #             self.labels[0] += 1
        #             self.labels[int(self.labels[0])] = self.labels[0]
        #             self.cluster[i] = self.labels[0]
        #         elif cluster == 1:
        #             # Next to one cluster so set to the cluster number
        #             # (one of left or top will be zero)
        #             self.cluster[i] = max(top, left)
        #         elif cluster == 2:  # Next to two clusters
        #             self.cluster[i] = self._union(top, left)

        # self.labels[self.labels[0]] = 0 # This is links emtyp cells to zero, makes them not drawn
        # self.labels[0] = 0 # Stops infinite loop in find function
        # self.cluster = self._find(self.cluster) # Give each cluster a unique label

    def _is_infinite(self) -> int:
        """Check if the grid is infinite"""
        # Find cluster numbers on top and bottom
        top_bot = np.intersect1d(
            self.cluster[: self.grid_size],
            self.cluster[self.grid.size - self.grid_size :],
        )
        # Find cluster numbers on left and right
        left_right = np.intersect1d(
            self.cluster[self.grid_size - 1 :: self.grid_size],
            self.cluster[0 :: self.grid_size],
        )
        # Remove empty sites
        top_bot = top_bot[top_bot != 0]
        left_right = left_right[left_right != 0]
        # Returns 1 if a cluster belongs on opposite edges, 0 otherwise
        return int(left_right.size > 0 or top_bot.size > 0)