#! /usr/bin/env python

"""percolation.py: Monte Carlo Simulation of Percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui
import matplotlib.pyplot as plt

class Percolation:  # Class to handle percolation things
    def __init__(self, gui_man):
        self.name = "Site Percolation" # Name to store in dropdown menu
        self.grid_size = (self.grid_width, self.grid_height) = (100, 100) # Hardcoded grid size
        self.grid = np.zeros(self.grid_width * self.grid_height) # Grid values, 1 = active, 0 = deaded
        self.cluster = np.zeros_like(self.grid) # Init cluster values
        self.draw_call = False # Used to optimize draw calls
        # Add UI elements for this percolation
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
        self.draw_surface = pygame.Surface(self.grid_size) # Create surface to draw onto, for optimisation
        self.font = pygame.font.SysFont(None, 25) # Init font for drawing
        self.step() # Fill grid when initialising

    def draw(self, window_surf):
        if self.draw_call: # Only redraw grid if it has changed
            self.draw_surface.fill((255, 255, 255)) # Clear old grid
            for i in range(self.grid.size): #  Loop through all active sites and fill pixel black
                if self.grid[i] == 1:
                    self.draw_surface.set_at(
                        (i % self.grid_width, i // self.grid_height), (0, 0, 0)
                    )
            self.draw_call = False # No need to redraw now
        # Copy surface to main window
        window_surf.blit(
            pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60)
        )
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

    def hoshen_kopelman(self):
        self.cluster = self.grid[:]  # Array of sites and what cluster they're in
        links = [
            0
        ]  # Links clusters together that we're not previously found to be together

        for i in range(self.grid.size):
            if self.grid[i]:  # Loops through all the active sites
                top = (
                    0 if i % self.grid_width == 0 else self.cluster[i - 1]
                )  # Cluster number of left site
                left = (
                    0
                    if i // self.grid_width == 0
                    else self.cluster[i - self.grid_width]
                )  # Cluster number of top site

                c = int(top > 0) + int(left > 0)  # Counts how many sites are next to it
                if c == 0:  # If not in cluster, add to new one
                    links[0] += 1
                    links.append(links[0])
                    self.cluster[i] = links[0]
                elif (
                    c == 1
                ):  # Next to one cluster so set to the cluster number (one of left or top will be zero)
                    self.cluster[i] = max(top, left)
                elif c == 2:  # Next to two clusters
                    mx = max(top, left)  # Largest cluster index
                    mn = top + left - mx  # Lowest cluster index
                    links[mx] = mn  # Connects the largest index cluster to the lowest
                    self.cluster[i - 1] = mn  # Set left site to lowest index cluster
                    self.cluster[i - self.grid_width] = mn  # Set top site '' ''
                    self.cluster[i] = mn  # Set site '' ''

        label_dict = {0: 0}  # Dictionary to contain corrected indices
        for i in range(self.grid.size):
            if self.grid[i]:  # Loop through all sites again
                x = self.cluster[i]  # Get the old site index
                while x != links[x]:  # Moves through the links to the new correct index
                    x = links[x]
                if label_dict.get(x, -1) == -1:  # If the index is new to the dict
                    label_dict[x] = len(
                        label_dict
                    )  # Add on next integer value to end of dict as new index
                self.cluster[i] = label_dict[
                    x
                ]  # Set the site cluster number to this new index
        return len(label_dict) - 1  # Return the number of clusters (size of dictionary)

    def simulate(self):
        ps = np.linspace(0.0, 1.0, 1000)
        cs = np.zeros_like(ps)
        for i in range(ps.size):  # Loop through many values of p
            self.grid = (np.random.rand(self.grid.size) < ps[i]).astype(
                np.int
            )  # Create a random grid
            cs[i] = self.hoshen_kopelman()  # Find the number of clusters
        N = self.grid.size
        # Plot results from many simulations
        plt.plot(ps, cs)  # Plot the number of cluster vs the probability
        # A001168 - Number of fixed polyominoes with n cells. 
        coeffs = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446, 135268, 505861, 1903890, 7204874, 27394666, 104592937, 400795844, 1540820542, 5940738676, 22964779660, 88983512783, 345532572678, 1344372335524, 5239988770268, 20457802016011, 79992676367108]
        n_anyl = N * (sum([coeffs[i]*(ps**(i+1)) * (1-ps)**(i+2+2*round((i+1)**0.5)) for i in range(len(coeffs))]))
        plt.plot(ps, n_anyl, c = 'r')
        plt.xlabel("Site Probability")
        plt.ylabel("Cluster Size")
        plt.show()


# Create pygame window and gui manager
pygame.init()
pygame.display.set_caption("Percolation Simulation")
window_size = (window_width, window_height) = (720, 720)
window_surface = pygame.display.set_mode(window_size)


gui_manager = pygame_gui.UIManager(window_size)  # Initialize the GUI Manager

percolation_list = []  # List containing all the percolators that we make
percolation_list.append(Percolation(gui_manager))

perc_selector = (
    pygame_gui.elements.UIDropDownMenu(  # Drop down menu to select percolator
        [p.name for p in percolation_list],
        percolation_list[0].name,
        pygame.Rect(10, 10, 600, 30),
        gui_manager,
    )
)
current_perc = (perc_selector.options_list).index(
    perc_selector.selected_option
)  # Hold index of current percolator

# Time keeping variables + misc.
is_running = True
is_playing = False
time_start = 0
time_end = 0.01
time_delta = 0.01

time_timer = 0.0

while is_running:  # Main loop for GUI
    # Calculates delta time
    time_end = pygame.time.get_ticks()
    time_delta = (time_end - time_start) / 1000.0
    time_start = time_end
    for event in pygame.event.get():  # Main event loop for pygame
        if event.type == pygame.QUIT:  # Handle QUIT event
            is_running = False
        if event.type == pygame.USEREVENT:
            if (
                event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
            ):  # Changes the current percolator if drop down menu is changed
                current_perc = (perc_selector.options_list).index(
                    perc_selector.selected_option
                )
        percolation_list[current_perc].process_events(event)
        gui_manager.process_events(event)  # Update the events for gui

    # Update GUI with delta time
    gui_manager.update(time_delta)
    percolation_list[current_perc].update(time_delta)

    # Draw all the GUI
    window_surface.fill((44, 47, 51))
    percolation_list[current_perc].draw(window_surface)
    gui_manager.draw_ui(window_surface)
    pygame.display.update()