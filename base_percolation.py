"""The shared logic between multiple simulation classes which inherit from this"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui


class BasePercolation:
    """Base class for a percolation simulation"""

    def __init__(self, *, name: str, grid_size: int) -> None:
        """
        name: the name of the simulation in the dropdown
        grid_size: the number of cells on a row/column (the lattice is square)
        gui_man: pygame gui manager to handle user events
        """
        self.name = name
        self.draw_call = False
        self.grid_size = grid_size

        # Grid values, 1 = active, 0 = deaded
        self.grid = np.zeros(self.grid_size ** 2, np.int)  

    def draw(self, window_surf: pygame.Surface):
        pass

    def process_events(self, event: pygame.event.Event):
        pass

    def update(self, delta: float):
        pass

    def enable(self, gui_manager: pygame_gui.UIManager):
        pass
