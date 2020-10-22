#! /usr/bin/env python

"""percolation.py: Monte Carlo Simulation of Percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import numpy as np
import pygame
import pygame_gui
import matplotlib.pyplot as plt


class Percolation:
    def __init__(self, gui_manager):
        self.gui_manager = gui_manager
        self.grid_size = (self.grid_width, self.grid_height) = (400, 400)
        self.number_of_sites = self.grid_width * self.grid_height
        self.grid = np.zeros(self.number_of_sites, np.int8)
        self.cluster = np.zeros_like(self.grid, np.int)
        self.step_func = self._square_perc_step
        self.draw_call = False
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

    def draw(self, window_surf):
        if self.draw_call:
            self.draw_surface.fill((255, 255, 255))
            for i in range(self.grid.size):
                if self.grid[i] == 1:
                    self.draw_surface.set_at(
                        (i % self.grid_width, i // self.grid_height), (0, 0, 0)
                    )
            self.draw_call = False
        window_surf.blit(
            pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60)
        )
        img = self.font.render(
            f"p: {self.p_slider.current_value:.3f}", True, (255, 255, 255), None
        )
        window_surf.blit(img, (300 - img.get_rect().width // 2, 690))

    def _square_perc_step(self):
        self.cluster = np.zeros_like(self.grid, np.int)
        self.grid = np.random.rand(self.number_of_sites) < self.p_slider.current_value
        self.draw_call = True
        self.draw_path = False

    def GridAt(self,x,y):
        if x < 0 or x > self.grid_width: return 0
        if y < 0 or y > self.grid_height: return 0
        return int(self.grid[x+ y*self.grid_width])

    def hoshen_kopelman(self):
        self.cluster = self.grid.astype(np.int)
        links = [0]

        for i in range(self.number_of_sites):
            if self.grid[i]:
                top = 0 if i%self.grid_width == 0 else self.cluster[i-1]
                left = 0 if i//self.grid_width == 0 else self.cluster[i-self.grid_width]

                c = int(top>0) + int(left>0)
                if c == 0:
                    links[0] += 1
                    links.append(links[0])
                    self.cluster[i] = links[0]
                elif c == 1:
                    self.cluster[i] = max(top,left)
                elif c == 2:
                    mx =  max(top,left)
                    mn = top+left-mx
                    links[mx] = mn
                    self.cluster[i-1] = mn
                    self.cluster[i-self.grid_width] = mn
                    self.cluster[i] = mn
        
        label_dict = {0:0}
        for i in range(self.number_of_sites):
            if self.grid[i]:
                x = self.cluster[i]
                while x != links[x]:
                    x = links[x]
                if label_dict.get(x,-1) == -1:
                    label_dict[x] = len(label_dict)
                self.cluster[i] = label_dict[x]
        return len(label_dict)
        
    def simulate(self):
        ps = np.linspace(0.0,1.0,1000)
        cs = np.zeros_like(ps)
        for i in range(ps.size):
            print(f"{i/ps.size:.3f}")
            self.grid = np.random.rand(self.number_of_sites) < ps[i]
            cs[i] = self.hoshen_kopelman()
        plt.plot(ps,cs)
        plt.xlabel("Site Probability")
        plt.ylabel("Cluster Size")
        plt.show()

        

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
    pygame.Rect(620, 180, 90, 50), "Cluster", gui_manager
)

button_graph = pygame_gui.elements.UIButton(
    pygame.Rect(620,240,90,50), "Plot", gui_manager
)

perc_manager = Percolation(gui_manager)
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
                    perc_manager.hoshen_kopelman()
                elif event.ui_element == button_graph:
                    perc_manager.simulate()
            

        gui_manager.process_events(event)

    time_timer += time_delta
    if time_timer > 0.5:
        time_timer -= 0.5
        if is_playing:
            perc_manager.step_func()

    gui_manager.update(time_delta)

    window_surface.fill((44, 47, 51))
    perc_manager.draw(window_surface)
    gui_manager.draw_ui(window_surface)
    pygame.display.update()
