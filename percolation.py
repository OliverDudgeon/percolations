#! /usr/bin/env python

"""percolation.py: Monte Carlo Simulation of Percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui


class Percolation:
    def __init__(self, gui_manager, window_size):
        (window_width, window_height) = window_size
        self.gui_manager = gui_manager
        self.window_size = window_size
        self.grid_size = (self.grid_width, self.grid_height) = (400, 400)
        self.grid = 255 * np.ones([self.grid_width, self.grid_height, 3])
        self.p_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((10, 670), (600, 20)),
            0.0,
            (0.0, 1.0),
            gui_manager,
        )
        self.draw_surface = pygame.Surface(self.grid_size)
        self.font = pygame.font.SysFont(None, 25)

        self.perc_selector = pygame_gui.elements.UIDropDownMenu(
            ["Square Site Percolation"],
            "Square Site Percolation",
            pygame.Rect(10, 10, 600, 30),
            gui_manager,
        )

    def Draw(self, window_surf):
        pygame.surfarray.blit_array(self.draw_surface, self.grid)
        window_surf.blit(
            pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60)
        )
        img = self.font.render(
            f"p: {self.p_slider.current_value:.3f}", True, (255, 255, 255), None
        )
        window_surf.blit(img, (300 - img.get_rect().width // 2, 690))

    def GenRandomStart(self):
        rand_points = (np.random.rand(self.grid_width,self.grid_height)>=0.25).reshape((self.grid_width,self.grid_width,1))
        self.grid = np.repeat(rand_points,3,axis = 2)*255


# Create pygame window and gui manager
pygame.init()
pygame.display.set_caption("Percolation Simulation")
window_size = (window_width, window_height) = (720, 720)
window_surface = pygame.display.set_mode(window_size)
gui_manager = pygame_gui.UIManager(window_size)

perc_manager = Percolation(gui_manager, window_size)
perc_manager.GenRandomStart()

is_running = True
time_start = 0
time_end = 0.01
time_delta = 0.01

while is_running:
    time_end = pygame.time.get_ticks()
    time_delta = time_end - time_start
    time_start = time_end
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        gui_manager.process_events(event)

    gui_manager.update(time_delta)

    window_surface.fill((44, 47, 51))
    perc_manager.Draw(window_surface)
    gui_manager.draw_ui(window_surface)
    pygame.display.update()
