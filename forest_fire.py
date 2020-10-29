"""Simulation of the forest fire percolation model"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UITextEntryLine, UIButton, UIDropDownMenu
import matplotlib.pyplot as plt

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
        self.is_simulating = False
        self.plot_option_mean = self.plot_option_raw = self.plot_option_order = False
        self.iterative_tree_frac = 0
        self.step_iteration = 0
        self.probabilities = 25 # Edit number of data points in plots
        self.sim_reps = 20 # Edit the number of repeats
        self.sim_times = np.zeros((1,self.probabilities))
        self.full_sim_times = np.zeros((self.sim_reps,self.probabilities))
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
        self.button_sim = UIButton(pygame.Rect(540, 700, 90, 50), "Simulate", gui_manager)
        self.menu_plot = UIDropDownMenu(("Plot mean","Plot raw data","Plot order parameter"),"Plot mean",
                                        pygame.Rect(490,750,190,20),gui_manager)
                                         
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
            if event.ui_element == self.button_sim:
                self.is_playing = False
                if self.menu_plot.selected_option == ("Plot mean"):
                    self.plot_option_mean = True # Plot mean values
                    self.plopt_option_raw = self.plot_option_order = False
                    self.init_sim()
                elif self.menu_plot.selected_option == ("Plot raw data"):
                    self.plot_option_raw = True # Plot raw data
                    self.plopt_option_mean = self.plot_option_order = False
                    self.init_sim()
                else:
                    self.plot_option_order = True # Plot order parameter (also plots mean but much slower)
                    self.plopt_option_mean = self.plot_option_raw = False
                    self.full_order_parameter_array = np.zeros_like(self.full_sim_times)
                    self.order_parameter_array = np.zeros_like(self.sim_times)
                    self.init_sim()
                
        elif event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            self.is_playing = False
            self.button_play.set_text("Play")
            if self.validate_entries():
                self.generate_random_start()
                

    def init_sim(self):
        """Produce plots of critical behaviour in a modified algorithm"""
        # Repeat algorithm multiple times 
        for i1 in range(0,self.sim_reps):
            # Perform calculation for multiple tree coverage fractions
            for i2 in range(1,self.probabilities):
                self.iterative_tree_frac = i2/self.probabilities
                self.is_simulating = True
                self.generate_random_start()
                while self.is_simulating == True:
                    self.sim_step()
            print(self.sim_times)
            self.full_sim_times[i1,:] = self.sim_times
            if self.plot_option_order == True:
                self.full_order_parameter_array[i1,:] = self.order_parameter_array
            
        # Save data (probably not necessary anymore)
        sim_times_final = np.mean(self.full_sim_times, axis = 0)
        print(sim_times_final)
        if self.plot_option_raw == True: # If plotting raw data the figure and axes already exist
            plt.xlabel("Initial tree fraction")
            plt.ylabel("Time until simulation complete")
        else:
            # Make array of tree coverage fractions used
            x_probs = np.linspace(0,1,np.size(sim_times_final)).reshape((self.probabilities,1))
            # Plot mean
            plt.figure(1)
            plt.plot(x_probs,np.transpose(sim_times_final),'k*')
            plt.xlabel("Initial tree fraction")
            plt.ylabel("Mean time until simulation complete")
            if self.plot_option_order == True:
                # Plot order parameter on separate figure
                order_parameter_final = np.mean(self.full_order_parameter_array, axis = 0)
                plt.figure(2)
                plt.plot(x_probs,np.transpose(order_parameter_final),'k*')
                plt.xlabel("Initial tree fraction")
                plt.ylabel("Order parameter")
    
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
        # Need different starts depending on whether playing or simulating
        if self.is_simulating == False:
            # Places random trees randomly in array
            tree_fraction = float(self.tree_fraction_entry.get_text())
            self.grid = (np.random.rand(self.grid.size) < tree_fraction).astype(np.int)

            # Outer edges of grid set to be empty - this simplifies
            # fire spread code (see Burning)
            self.reset_outer_edges()

            self.draw_call = True
        else:
            self.step_iteration = 0
            # Place trees randomly, with probabiliity from the loop in init_sim
            tree_fraction = self.iterative_tree_frac
            self.grid = (np.random.rand(self.grid.size) < tree_fraction).astype(np.int)
            # Set 2nd row on fire 
            self.grid[self.grid_size : 2*self.grid_size-1] = 2
            self.reset_outer_edges()

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

    def sim_step(self):
        # Modified version of step for criticality simulation. No tree growth,
        # no spontaneous fires, and fires only spread via nearest-neighbours
        # (i.e. no North East, South West etc) so that results can be compared 
        # with square site percolation
        key_index = int(self.iterative_tree_frac*self.probabilities)
        self.test_grid = self.grid
        for i in range(self.grid.size - self.grid_size - 1):
            point = self.grid[i]
            north = self.grid[i - self.grid_size]
            east = self.grid[i + 1]
            south = self.grid[i + self.grid_size]
            west = self.grid[i - 1]
            if point == 2:
                self.grid[i - self.grid_size] = -2 if north else north
                self.grid[i + 1] = -2 if east else east
                self.grid[i + self.grid_size] = -2 if south else south
                self.grid[i - 1] = -2 if west else west
                
                self.grid[i] = 0
                
        self.step_iteration += 1
        print(self.step_iteration)
        self.grid = np.absolute(self.grid)
        self.reset_outer_edges()
        last_line = self.grid[self.grid_size^2-2*self.grid_size : self.grid_size^2-self.grid_size-1]
        # Algorithm complete if fire has spread to last line
        if 2 in last_line:
            self.is_simulating = False
            self.sim_times[0,key_index] = self.step_iteration
            print("ALL THE WAY")
            if self.plot_option_raw == True:
                # Plot raw data
                plt.plot(self.iterative_tree_frac,self.step_iteration,'k.')
            if self.plot_option_order == True:
                # Work out fraction of grid that's burning, remembering to 
                # remove the outer edges
                number_of_fires = np.count_nonzero(np.where(self.grid == 2,2,0))
                self.order_parameter_array[0,key_index] = number_of_fires/((self.grid_size-2)^2)
        # Algorithm complete if grid doesn't change (fire can't reach new trees)
        if np.all(self.test_grid == self.grid):
            self.is_simulating = False
            self.sim_times[0,key_index] = self.step_iteration
            print("BURNED ITSELF OUT")
            if self.plot_option_raw == True:
                #Plot raw data
                plt.plot(self.iterative_tree_frac,self.step_iteration,'r.')
            if self.plot_option_order == True:
                # Work out fraction of grid that's burning, remembering to 
                # remove the outer edges
                number_of_fires = np.count_nonzero(np.where(self.grid == 2,2,0))
                self.order_parameter_array[0,key_index] = number_of_fires/((self.grid_size-2)^2)
