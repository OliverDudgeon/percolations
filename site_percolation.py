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
        # Add UI elements for this percolation

        # Create surface to draw onto, for optimisation
        self.draw_surface = pygame.Surface(self.grid_size)
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
                    # Transform index of 1D array to 2D array
                    x_pos, y_pos = (i % self.grid_width, i // self.grid_height)
                    surface.set_at((x_pos, y_pos), BLACK)

            self.draw_call = False  # No need to redraw now
        # Copy surface to main window
        window_surf.blit(pygame.transform.scale(surface, (600, 600)), (10, 60))

        # Draw the value of the probability slider
        text = f"p: {self.p_slider.current_value:.3f}"
        img = self.font.render(text, True, WHITE, None)
        window_surf.blit(img, (300 - img.get_rect().width // 2, 690))

    def process_events(self, event: pygame.event.Event):
        if event.type == pygame.USEREVENT:
            # Handle pygame_gui button events
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.button_step:
                    self.step()
                elif event.ui_element == self.button_path:
                    self.hoshen_kopelman()
                elif event.ui_element == self.button_graph:
                    self.simulate()

    def update(self, delta) -> None:
        return

    def hoshen_kopelman(self) -> int:
        """
        Implementation of the Hoshen-Kopelman clustering algorithm

        returns the number of clusters found
        """
        self.cluster = self.grid[:]  # Array of sites and what cluster they're in

        # Links clusters together that we're not previously found to be together
        links = [0]

        for i in range(self.grid.size):
            column = i % self.grid_width
            row = i // self.grid_width
            if self.grid[i]:  # Loops through all the *active* sites

                # Cluster number of left site
                top = int(0 if column == 0 else self.cluster[i - 1])

                # Cluster number of top site
                left = int(0 if row == 0 else self.cluster[i - self.grid_width])

                # Counts how many sites are next to it
                num_adjacent_sites = int(top > 0) + int(left > 0)
                if num_adjacent_sites == 0:
                    # If not in cluster, add to new one
                    links[0] += 1
                    links.append(links[0])
                    self.cluster[i] = links[0]
                elif num_adjacent_sites == 1:
                    # Next to one cluster so set to the cluster number
                    # (one of left or top will be zero)
                    self.cluster[i] = max(top, left)
                elif num_adjacent_sites == 2:
                    # Next to two clusters
                    max_cluster_index = max(top, left)
                    min_cluster_index = top + left - max_cluster_index

                    # Connects the largest index cluster to the lowest
                    links[max_cluster_index] = min_cluster_index

                    # Set left site to lowest index cluster
                    self.cluster[i - 1] = min_cluster_index
                    # Set top site '' ''
                    self.cluster[i - self.grid_width] = min_cluster_index
                    # Set site '' ''
                    self.cluster[i] = min_cluster_index

        label_dict = {0: 0}  # Dictionary to contain corrected indices
        for i in range(self.grid.size):
            if self.grid[i]:  # Loop through all sites again
                old_index = self.cluster[i]

                # Moves through the links to the new correct index
                while old_index != links[old_index]:
                    old_index = links[old_index]
                if label_dict.get(old_index, -1) == -1:
                    # If the index is new to the dict
                    # Add on next integer value to end of dict as new index
                    label_dict[old_index] = len(label_dict)
                # Set the site cluster number to this new index
                self.cluster[i] = label_dict[old_index]
        return len(label_dict) - 1  # Return the number of clusters (size of dictionary)

    def simulate(self):
        """Generate the graph of cluster size against site probability"""
        probs = np.linspace(0.0, 1.0, 1000)
        clusters = np.zeros_like(probs)

        for i in range(probs.size):  # Loop through many values of p
            # Create a random grid
            self.grid = (np.random.rand(self.grid.size) < probs[i]).astype(np.int)
            clusters[i] = self.hoshen_kopelman()  # Find the number of clusters
        # Plot results from many simulations
        plt.plot(probs, clusters)  # Plot the number of cluster vs the probability
        # A001168 - Number of fixed polyominoes with n cells.

        calc = (
            lambda i: COEFFS[i]
            * (probs ** (i + 1))
            * (1 - probs) ** (i + 2 + 2 * round((i + 1) ** 0.5))
        )

        n_anyl = self.grid.size * (sum([calc(i) for i in range(len(COEFFS))]))
        n_anyl1 = self.grid.size * (sum([calc(i) for i in range(20)]))
        plt.plot(probs, n_anyl, c="r")
        plt.plot(probs, n_anyl1, c="g")
        plt.xlabel("Site Probability")
        plt.ylabel("Cluster Size")
        plt.show()
