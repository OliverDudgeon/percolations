#! /usr/bin/env python

"""percolation.py: Monte Carlo Simulation of Percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import pygame
import pygame_gui
from typing import List

from base_percolation import BasePercolation
from site_percolation import SitePercolation
from forest_fire import ForestFire


if __name__ == "__main__":
    # Create pygame window and gui manager
    pygame.init()
    pygame.display.set_caption("Percolation Simulation")
    window_size = (window_width, window_height) = (720, 850)
    window_surface = pygame.display.set_mode(window_size)

    gui_manager = pygame_gui.UIManager(window_size)  # Initialize the GUI Manager

    percolation_list: List[BasePercolation] = [
        SitePercolation(),
        ForestFire(),
    ]  # List containing all the percolators that we make

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
    percolation_list[current_perc].enable(gui_manager)
    # Time keeping variables + misc.
    is_running = True
    time_start = 0
    time_end = 0.01
    time_delta = 0.01

    while is_running:  # Main loop for GUI
        # Calculates delta time
        time_end = pygame.time.get_ticks()
        time_delta = (time_end - time_start) / 1000.0
        time_start = time_end
        for event in pygame.event.get():  # Main event loop for pygame
            if event.type == pygame.QUIT:
                is_running = False  # Handle QUIT event
            if event.type == pygame.USEREVENT:
                if (
                    event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
                ):  # Changes the current percolator if drop down menu is changed
                    gui_manager.clear_and_reset()
                    current_perc = (perc_selector.options_list).index(
                        perc_selector.selected_option
                    )
                    perc_selector = pygame_gui.elements.UIDropDownMenu(  # Drop down menu to select percolator
                        [p.name for p in percolation_list],
                        percolation_list[current_perc].name,
                        pygame.Rect(10, 10, 600, 30),
                        gui_manager,
                    )
                    percolation_list[current_perc].enable(gui_manager)
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
