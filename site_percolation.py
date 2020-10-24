import numpy as np
import pygame
import pygame_gui
import matplotlib.pyplot as plt
import time

from base_percolation import BasePercolation


class SitePercolation(BasePercolation):
    """Class to handle percolation things."""

    def __init__(self):
        super().__init__(name="Site Percolation", grid_size=1000)
        self.cluster = np.zeros_like(self.grid)  # Init cluster values
        self.draw_call = False  # Used to optimize draw calls
        self.draw_cluster = False
        # Add UI elements for this percolation
        self.draw_surface = pygame.Surface(
            (self.grid_size,self.grid_size)
        )  # Create surface to draw onto, for optimisation
        self.font = pygame.font.SysFont(None, 25)  # Init font for drawing

    def enable(self, gui_man):
        self.p_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((10, 670), (600, 20)),
            0.25,
            (0.0, 1.0),
            gui_man,
        )
        self.button_step = pygame_gui.elements.UIButton(
            pygame.Rect(620, 60, 90, 50), "Step", gui_man
        )
        self.button_path = pygame_gui.elements.UIButton(
            pygame.Rect(620, 120, 90, 50), "Cluster", gui_man
        )
        self.button_graph = pygame_gui.elements.UIButton(
            pygame.Rect(620, 180, 90, 50), "Plot", gui_man
        )
        self.step()

    def draw(self, window_surf):
        if self.draw_call:  # Only redraw grid if it has changed
            self.draw_surface.fill((255, 255, 255))  # Clear old grid
            for i in range(
                self.grid.size
            ):  #  Loop through all active sites and fill pixel black
                if self.grid[i] == 1:
                    self.draw_surface.set_at(
                        (i % self.grid_size, i // self.grid_size), (0, 0, 0)
                    )
            self.draw_call = False  # No need to redraw now
        # Copy surface to main window
        window_surf.blit(
            pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60)
        )

        if self.draw_clusters:
            s = 600//self.grid_size
            for i in range(self.grid.size):
                if not self.cluster[i]: continue
                img = self.font.render(str(self.cluster[i]),True,(255,0,0),None)
                c = (10 + (i%self.grid_size)*s,60 +(i//self.grid_size)*s)
                window_surf.blit(pygame.transform.smoothscale(img, (600//self.grid_size,600//self.grid_size)), c)

        # Draw the value of the probability slider
        img = self.font.render(
            f"p: {self.p_slider.current_value:.3f}", True, (255, 255, 255), None
        )
        window_surf.blit(img, (300 - img.get_rect().width // 2, 690))

    def process_events(self, e):
        if e.type == pygame.USEREVENT:
            if (
                e.user_type == pygame_gui.UI_BUTTON_PRESSED
            ):  # Handle pygame_gui button events
                if e.ui_element == self.button_step:
                    self.step()
                elif e.ui_element == self.button_path:
                    self.hoshen_kopelman()
                    self.draw_clusters = True
                elif e.ui_element == self.button_graph:
                    self.simulate()

    def update(self, delta):
        return

    def step(self):  # Do one step of the simulation
        self.cluster = np.zeros_like(self.grid, np.int)  # Reset cluster values
        self.grid = (
            np.random.rand(self.grid.size) < self.p_slider.current_value
        )  # Repopulate sites
        self.draw_call = True  # Call a redraw
        self.draw_clusters = False

    def hoshen_kopelman(self):
        self.cluster = self.grid.astype(np.int)  # Array of sites and what cluster they're in
        labels = np.array([0 for l in range(self.grid.size//2)])  # Links clusters together that we're not previously found to be together

        def find(x):
            y = x
            while (labels[y] != y).any():
                y = labels[y]
            
            while (labels[x] != x).any():
                z = labels[x]
                labels[x] = y
                x = z
            
            return y
        
        def union(x, y):
            fy = find(y)
            labels[find(x)] = fy
            return fy

        for i in range(self.grid.size):
            if self.grid[i]:  # Loops through all the active sites
                top = (
                    0 if i % self.grid_size == 0 else self.cluster[i - 1]
                )  # Cluster number of left site
                left = (
                    0
                    if i // self.grid_size == 0
                    else self.cluster[i - self.grid_size]
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
        self.cluster = find(self.cluster)
        top_bot = np.intersect1d(self.cluster[:self.grid_size], self.cluster[self.grid.size - self.grid_size :])
        left_right = np.intersect1d(self.cluster[self.grid_size - 1 :: self.grid_size], self.cluster[0 :: self.grid_size])
        top_bot = top_bot[top_bot != 0]
        left_right = left_right[left_right != 0]
        if top_bot.size > 0: return 1
        if left_right.size > 0: return 1
        return 0

    def simulate(self):
        top = 0
        bot = 0
        for l in range(100):
            self.grid = (np.random.rand(self.grid.size) < 0.60).astype(np.int)
            top += self.hoshen_kopelman()
        print("half")
        for l in range(100):
            self.grid = (np.random.rand(self.grid.size) < 0.59).astype(np.int)
            bot += self.hoshen_kopelman()
        print((0.59*bot + 0.60*top)/(top+bot))
