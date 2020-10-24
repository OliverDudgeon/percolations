"""Simulation of a 2D square site lattice percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIHorizontalSlider
import matplotlib.pyplot as plt

from base_percolation import BasePercolation
from coefficients import COEFFS

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BTN_WH = (90, 50)


class SitePercolation(BasePercolation):
    """Class to handle percolation things."""

    def __init__(self):
        super().__init__(name="Site Percolation", grid_size=100)

        self.cluster = np.zeros_like(self.grid)  # Init cluster values
        self.draw_call = False  # Used to optimize draw calls
        self.draw_cluster = False
        # Add UI elements for this percolation

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
        self.grid = np.random.rand(self.grid.size) < self.p_slider.current_value
        self.draw_call = True  # Call a redraw

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
                if self.grid[i] == 1:
                    self.draw_surface.set_at(
                        (i % self.grid_size, i // self.grid_size), (0, 0, 0)
                    )
            self.draw_call = False  # No need to redraw now
        # Copy surface to main window
        window_surf.blit(
            pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60)
        )
        # Copy surface to main window
        window_surf.blit(pygame.transform.scale(surface, (600, 600)), (10, 60))

        if self.draw_clusters:
            s = 600 // self.grid_size
            for i in range(self.grid.size):
                if not self.cluster[i]:
                    continue
                img = self.font.render(str(self.cluster[i]), True, (255, 0, 0), None)
                c = (10 + (i % self.grid_size) * s, 60 + (i // self.grid_size) * s)
                window_surf.blit(
                    pygame.transform.smoothscale(
                        img, (600 // self.grid_size, 600 // self.grid_size)
                    ),
                    c,
                )
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

    def step(self):  # Do one step of the simulation
        self.cluster = np.zeros_like(self.grid, np.int)  # Reset cluster values
        self.grid = (
            np.random.rand(self.grid.size) < self.p_slider.current_value
        )  # Repopulate sites
        self.draw_call = True  # Call a redraw
        self.draw_clusters = False

    def hoshen_kopelman(self):
        """
        Implementation of the Hoshen-Kopelman clustering algorithm
        returns the number of clusters found
        """
        self.cluster = self.grid.astype(
            np.int
        )  # Array of sites and what cluster they're in
        labels = np.array(
            [0 for l in range(self.grid.size // 2)]
        )  # Links clusters together that we're not previously found to be together

        def find(x):  # Loops through labels indexing them correctly
            y = x
            while (labels[y] != y).any():
                y = labels[y]

            while (labels[x] != x).any():
                z = labels[x]
                labels[x] = y
                x = z
            return y

        def union(x, y):  # Links to cluster together
            fy = find(y)
            labels[find(x)] = fy
            return fy

        for i in range(self.grid.size):
            if self.grid[i]:  # Loops through all the active sites
                top = (
                    0 if i % self.grid_size == 0 else self.cluster[i - 1]
                )  # Cluster number of left site
                left = (
                    0 if i // self.grid_size == 0 else self.cluster[i - self.grid_size]
                )  # Cluster number of top site

                c = int(top > 0) + int(left > 0)  # Counts how many sites are next to it
                if c == 0:  # If not in cluster, add to new one
                    labels[0] += 1
                    labels[labels[0]] = labels[0]
                    self.cluster[i] = labels[0]
                elif (
                    c == 1
                ):  # Next to one cluster so set to the cluster number (one of left or top will be zero)
                    self.cluster[i] = max(top, left)
                elif c == 2:  # Next to two clusters
                    self.cluster[i] = union(top, left)
        labels[0] = 0
        self.cluster = find(self.cluster)  # Finds all the unique labels for clusters

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
        # Returns 1 if a cluster belongs on opposite edges
        if top_bot.size > 0:
            return 1
        if left_right.size > 0:
            return 1
        return 0

    def simulate(self):
        # To find critical point WIP
        top = 0
        bot = 0
        for l in range(100):
            self.grid = (np.random.rand(self.grid.size) < 0.60).astype(np.int)
            top += self.hoshen_kopelman()
        for l in range(100):
            self.grid = (np.random.rand(self.grid.size) < 0.59).astype(np.int)
            bot += self.hoshen_kopelman()
        print((0.59 * bot + 0.60 * top) / (top + bot))
