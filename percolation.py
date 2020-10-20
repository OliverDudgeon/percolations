#! /usr/bin/env python

"""percolation.py: Monte Carlo Simulation of Percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui
from functools import reduce


class Percolation:
    def __init__(self, gui_manager, window_size):
        (window_width, window_height) = window_size
        self.gui_manager = gui_manager
        self.window_size = window_size
        self.grid_size = (self.grid_width, self.grid_height) = (10, 10)
        self.max_array_length = self.grid_width * self.grid_height
        self.grid = np.array([])
        self.grid_path = np.array([])
        self.step_func = self.__SquarePercStep
        self.draw_call = False
        self.draw_path = False
        self.p_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((10, 670), (600, 20)),
            0.25,
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
        self.step_func()

    def Draw(self, window_surf):
        if self.draw_call:
            self.draw_surface.fill((255, 255, 255))
            for index in self.grid:
                self.draw_surface.set_at(
                    (index % self.grid_width, index // self.grid_width), (0, 0, 0)
                )
            self.draw_call = False
        if self.draw_path:
            for index in self.grid_path:
                self.draw_surface.set_at(
                    (index % self.grid_width, index // self.grid_width), (255, 0, 0)
                )
        window_surf.blit(
            pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60)
        )
        img = self.font.render(
            f"p: {self.p_slider.current_value:.3f}", True, (255, 255, 255), None
        )
        window_surf.blit(img, (300 - img.get_rect().width // 2, 690))

    def __SquarePercStep(self):
        self.grid = np.where(
            np.random.rand(self.max_array_length) < self.p_slider.current_value
        )[0]
        self.grid_path = []
        self.draw_call = True
        self.draw_path = False

    def __FindPathStep(self, current, old=np.array([])):
        start_next = [current - self.grid_width]
        if (current-1)//self.grid_width == current//self.grid_width: start_next += [current-1]
        if (current+1)//self.grid_width == current//self.grid_width: start_next += [current+1]
        neighbour = np.intersect1d(
            np.array(start_next), self.grid
        )
        
        nexts = np.setdiff1d(neighbour, old)
        for index in nexts:
            if index < self.grid_width:
                return [index]
            new_old = np.concatenate((old, [index]))
            return [index] + self.__FindPathStep(index, new_old)
        return [-1]

    def FindPath(self):
        self.draw_path = not self.draw_path
        if len(self.grid_path) > 0 or not self.draw_path: return
        row_bot = self.grid[
            np.where(self.grid > self.max_array_length - self.grid_width)
        ]
        for index in row_bot:
            p = [index] + self.__FindPathStep(index, [])
            if -1 not in p:
                self.grid_path = p
                break
        


# Create pygame window and gui manager
pygame.init()
pygame.display.set_caption("Percolation Simulation")
window_size = (window_width, window_height) = (720, 720)
window_surface = pygame.display.set_mode(window_size)
gui_manager = pygame_gui.UIManager(window_size)

button_step = pygame_gui.elements.UIButton(
    pygame.Rect(620, 60, 90, 50), "Step", gui_manager
)
button_play = pygame_gui.elements.UIButton(
    pygame.Rect(620, 120, 90, 50), "Play", gui_manager
)

button_path = pygame_gui.elements.UIButton(
    pygame.Rect(620, 180, 90, 50), "Path", gui_manager
)

perc_manager = Percolation(gui_manager, window_size)

is_running = True
is_playing = False
time_start = 0
time_end = 0.01
time_delta = 0.01

time_timer = 0.0

while is_running:
    time_end = pygame.time.get_ticks()
    time_delta = (time_end - time_start) / 1000.0
    time_start = time_end
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button_step:
                    perc_manager.step_func()
                elif event.ui_element == button_play:
                    is_playing = not is_playing
                    if is_playing:
                        button_play.set_text("Pause")
                    else:
                        button_play.set_text("Play")
                elif event.ui_element == button_path:
                    perc_manager.FindPath()

        gui_manager.process_events(event)

    time_timer += time_delta
    if time_timer > 0.5:
        time_timer -= 0.5
        if is_playing:
            perc_manager.step_func()

    gui_manager.update(time_delta)

    window_surface.fill((44, 47, 51))
    perc_manager.Draw(window_surface)
    gui_manager.draw_ui(window_surface)
    pygame.display.update()
