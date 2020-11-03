"""Simulation of a 2D square site lattice percolation"""

__author__ = "Oliver Dudgeon, Adam Shaw, Joseph Parker"
__license__ = "MIT"

import time

import numpy as np
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIHorizontalSlider, UIDropDownMenu
import matplotlib.pyplot as plt
import matplotlib
from multiprocessing import Pool
from scipy.ndimage import measurements
from scipy.optimize import curve_fit

from base_percolation import BasePercolation

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BTN_WH = (90, 50)

GRID_CONTAINER_SIZE = 600
GRID_SIZE = 10
matplotlib.rcParams.update({"font.size": 22})


class SitePercolation(BasePercolation):
    """Class to handle percolation things."""

    def __init__(self):
        super().__init__(name="Site Percolation", grid_size=GRID_SIZE)

        self.cluster = np.zeros_like(self.grid, dtype=np.int)  # Init cluster values
        self.draw_call = False  # Used to optimize draw calls
        self.draw_clusters = False  # Used to draw clusters
        self.labels = np.zeros(
            self.grid.size // 2, dtype=np.int
        )  # Used for labeling clusters

        # Create surface to draw onto, for optimisation
        self.draw_surface = pygame.Surface((self.grid_size, self.grid_size))
        self.font = pygame.font.SysFont(None, 25)  # Init font for drawing

        self.p_slider = None
        self.button_step = None
        self.button_path = None
        self.button_graph = None

    def step(self):
        """Do one step of the simulation"""
        self.cluster = np.zeros_like(self.grid, dtype=np.int)  # Reset cluster values

        # Repopulate sites
        self.grid = (
            np.random.rand(self.grid.size) < self.p_slider.current_value
        ).astype(np.int)
        self.draw_call = True  # Call a redraw
        self.draw_clusters = False

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

        self.sim_select = UIDropDownMenu(
            ["Fisher Exponent", "Beta Exponent", "Critical Point", "Cluster Number"],
            "Fisher Exponent",
            pygame.Rect((10, 710, 200, 30)),
            gui_manager,
        )
        self.button_sim = UIButton(pygame.Rect(10, 750, *BTN_WH), "Plot", gui_manager)

        self.step()  # Initial draw

    def draw(self, window_surf) -> None:
        surface = self.draw_surface
        if self.draw_call:  # Only redraw grid if it has changed
            # Clear old grid by making every cell white
            surface.fill(WHITE)

            #  Loop through all active sites and fill pixel black
            for i in range(self.grid.size):
                row = i % self.grid_size
                column = i // self.grid_size
                if self.grid[i] == 1:
                    self.draw_surface.set_at((row, column), BLACK)
            self.draw_call = False  # No need to redraw now

        # Copy surface to main window
        window_surf.blit(
            pygame.transform.scale(
                self.draw_surface, (GRID_CONTAINER_SIZE, GRID_CONTAINER_SIZE)
            ),
            (10, 60),
        )
        # Copy surface to main window
        window_surf.blit(
            pygame.transform.scale(surface, (GRID_CONTAINER_SIZE, GRID_CONTAINER_SIZE)),
            (10, 60),
        )

        if self.draw_clusters:
            site_size = GRID_CONTAINER_SIZE // self.grid_size
            for i in range(self.grid.size):
                row = i % self.grid_size
                column = i // self.grid_size
                if not self.cluster[i]:
                    continue
                img = self.font.render(str(self.cluster[i]), True, RED, None)
                cluster = (10 + row * site_size, 60 + column * site_size)
                scaled = pygame.transform.smoothscale(img, (site_size, site_size))
                window_surf.blit(scaled, cluster)

                # Transform index of 1D array to 2D array
                pos = (i % self.grid_size, i // self.grid_size)
                surface.set_at(pos, BLACK)

        # Draw the value of the probability slider
        text = f"p: {self.p_slider.current_value:.3f}"
        img = self.font.render(text, True, WHITE, None)
        window_surf.blit(img, (300 - img.get_rect().width // 2, 690))

    def process_events(self, event: pygame.event.Event):
        # Handle pygame_gui button events
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button_step:
                self.step()
            elif event.ui_element == self.button_path:
                self.hoshen_kopelman()
                self.draw_clusters = True
            elif event.ui_element == self.button_sim:
                if self.sim_select.selected_option == "Fisher Exponent":
                    self._fisher_exponent()
                elif self.sim_select.selected_option == "Beta Exponent":
                    self._beta_exponent()
                elif self.sim_select.selected_option == "Critical Point":
                    self._sim_critical_point()
                elif self.sim_select.selected_option == "Cluster Number":
                    self._sim_cluster_number()

    def update(self, delta) -> None:
        return

    def _find(self, old_label):
        """Loops through labels indexing them correctly"""
        new_label = old_label
        while (self.labels[new_label] != new_label).any():
            new_label = self.labels[new_label]

        while (self.labels[old_label] != old_label).any():
            label = self.labels[old_label]
            self.labels[old_label] = new_label
            old_label = label
        return new_label

    def _union(self, label1, label2):
        """Links to cluster together"""
        label = self._find(label2)
        self.labels[self._find(label1)] = label
        return label

    def hoshen_kopelman(self):
        self.cluster, _ = measurements.label(
            self.grid.reshape((self.grid_size, self.grid_size))
        )
        self.cluster = self.cluster.reshape(self.grid.size)

    def _fisher_exponent(self):
        N = 40_000
        pc = 0.59274
        grid = np.random.rand(N, N) < pc + 0.0365
        labels, _ = measurements.label(grid)
        _, size = np.unique(labels, return_counts=True)
        size, counts = np.unique(size, return_counts=True)
        size = size[counts > N // 2]
        counts = counts[counts > N // 2] / np.sum(counts)

        def func(s, m, c):
            return m * s + c

        popt, pact = curve_fit(func, np.log(size), np.log(counts))
        print(-popt[0], pact[0])
        plt.figure(figsize=(10, 5))
        plt.plot(
            np.log(size),
            np.log(counts),
            "o",
            label="Data Points",
            color="black",
        )
        plt.plot(
            np.log(size),
            func(np.log(size), *popt),
            label="Linear Fit",
            linestyle="dashed",
            color="black",
            alpha=0.3,
        )
        plt.legend()
        plt.xlabel(r"$\log|s|$")
        plt.ylabel(r"$\log|n_{s}|$")
        plt.savefig("./site_data/tau_graph.pdf", format="pdf")
        plt.show()

    def _beta_exponent(self):
        size = 20000
        pc = 0.59274
        prob_list = np.linspace(pc, 0.7, 300)
        frac_list = np.zeros_like(prob_list)
        try:
            frac_list = np.load("./site_data/order_data.npy")
        except FileNotFoundError:
            for i in range(prob_list.size):
                print(i)
                grid = np.random.rand(size, size) < prob_list[i]
                labels, _ = measurements.label(grid)
                nlabel, count = np.unique(labels, return_counts=True)
                top_bot = np.intersect1d(labels[:][0], labels[:][size - 1])
                left_right = np.intersect1d(labels[0][:], labels[size - 1][:])
                for j in np.union1d(top_bot, left_right)[1:]:
                    frac_list[i] += count[np.where(nlabel == j)[0]] / (size * size)
            np.save("./site_data/order_data.npy", frac_list)
        prob_list -= pc
        frac_list = frac_list[prob_list > 0]
        prob_list = prob_list[prob_list > 0]

        prob_list = prob_list[frac_list > 0]
        frac_list = frac_list[frac_list > 0]
        np.log(frac_list)

        def func(x, m, c):
            return m * x + c

        fig = plt.figure(num=None, figsize=(10, 10))

        popt, pact = curve_fit(func, np.log(prob_list), np.log(frac_list))
        print(popt[0])
        plt.plot(prob_list, frac_list)
        plt.xlabel(r"|$p - p_{c}$|")
        plt.ylabel(r"P")
        # plt.title(
        #     r"Order parameter vs site probability for 2d site percolation, $P\sim|p-p_{c}|^{\beta}$"
        # )
        plt.legend(["Data"])

        plt.savefig("./site_data/order_fig.pdf", format="pdf")
        plt.savefig("./site_data/order_fig.svg", format="svg")
        plt.show()

        fig = plt.figure(num=None, figsize=(10, 10))

        plt.plot(np.log(prob_list), np.log(frac_list))
        plt.plot(np.log(prob_list), func(np.log(prob_list), *popt))
        plt.xlabel(r"$\log |p-p_{c}|$")
        plt.ylabel(r"$\log P$")
        # plt.title(
        #     f"Log-Log plot of order parameter vs site probability to find beta exponent $\\beta = {popt[0]}$"
        # )
        plt.legend(["Data", "Linear Regression"])
        plt.show()

    def _sim_critical_point(self):
        """To find critical point WIP"""
        p_low = 0.0
        p_high = 1.0
        N = 40_000
        ph_list = [1.0]
        pl_list = [0.0]
        try:
            ph_list = np.load("./site_data/ph_list.npy")
            pl_list = np.load("./site_data/pl_list.npy")
        except FileNotFoundError:
            while abs(p_high - p_low) > 0.0001:
                p = (p_high + p_low) / 2
                grid = np.random.rand(N, N) < p
                labels, _ = measurements.label(grid)
                inf_labels = np.union1d(
                    np.intersect1d(labels[:][0], labels[:][N - 1]),
                    np.intersect1d(labels[0][:], labels[N - 1][:]),
                )
                inf_labels = inf_labels[np.where(inf_labels != 0)]
                if inf_labels.size > 0:
                    p_high = p
                else:
                    p_low = p
                print(p_low, p_high)
                ph_list.append(p_high)
                pl_list.append(p_low)
            ph_list = np.asarray(ph_list)
            pl_list = np.asarray(pl_list)
            np.save("./site_data/ph_list.npy", ph_list)
            np.save("./site_data/pl_list.npy", pl_list)
        ns = np.arange(ph_list.size)
        p_c = (ph_list[-1] + pl_list[-1]) / 2.0
        pc_d = (ph_list[-1] - pl_list[-1]) / 2.0
        matplotlib.rcParams.update({"font.size": 24})
        plt.figure(num=None, figsize=(10, 6.5))
        plt.scatter(ns, ph_list, color="black", marker="^", label="Upper Probablilty")
        plt.scatter(ns, pl_list, color="black", label="Lower Probablilty")
        # plt.plot(ns, np.ones_like(ns) * p_c)
        plt.fill_between(ns, pl_list, ph_list, color="black", alpha=0.15)
        plt.legend()
        plt.xlabel("Iteration number")
        plt.ylabel("Probability")
        pc_str = f"{p_c:.4f}"
        pc_d_str = f"{pc_d:.1e}"
        # plt.title(
        #     r"Plot of binary search for critical probability, $p_{c} ="
        #     + pc_str
        #     + r"\pm"
        #     + pc_d_str
        #     + "$"
        # )
        plt.savefig("./site_data/critical_prob.pdf", format="pdf")
        plt.show()

    def _sim_cluster_number(self):
        N = 10_000
        prob_list = np.linspace(0, 1, 100)
        numb_list = np.zeros_like(prob_list)
        try:
            numb_list = np.load("./site_data/cluster_data.npy")
        except FileNotFoundError:
            for i in range(prob_list.size):
                print(i)
                grid = np.random.rand(N, N) < prob_list[i]
                label, counts = measurements.label(grid)
                numb_list[i] = counts
            np.save("./site_data/cluster_data.npy", numb_list)

        p = prob_list
        n = p * (1 - p) ** 4  # n = 1 term
        plt.plot(prob_list, numb_list / (10_000 * 10_000))
        plt.plot(p, n)
        n += 2 * p ** 2 * (1 - p) ** 6  # n = 2 term
        plt.plot(p, n)
        n += 2 * p ** 3 * (1 - p) ** 8 + 4 * p ** 3 * (1 - p) ** 7
        plt.plot(p, n)
        n += (
            2 * p ** 4 * (1 - p) ** 10
            + 4 * p ** 4 * (1 - p) ** 9
            + p ** 4 * (1 - p) ** 8
        )
        plt.plot(p, n)
        plt.legend(
            [
                "Data",
                "Polymioes curve n = 1",
                "Polymioes curve n = 2",
                "Polymioes curve n = 3",
                "Polymioes curve n = 4",
            ]
        )
        plt.xlabel("Site Probability")
        plt.ylabel("Number of clusters")
        plt.title("Number of clusters vs probability $n(p)$")
        plt.show()
