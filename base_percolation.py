import numpy as np
import pygame


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

        self.grid = np.zeros(
            self.grid_size**2, np.int
        )  # Grid values, 1 = active, 0 = deaded

    def draw(self, surf: pygame.Surface):
        pass

    def process_events(self, e: pygame.event):
        pass

    def update(self, delta: float):
        pass

    def enable(self, gui_manager):
        pass
