"""Parallel processed version of H-K algorithm"""

import numpy as np
from multiprocessing import Pool
from scipy.ndimage import measurements
import matplotlib.pyplot as plt

GRID_SIZE = 40000


def _is_infinite(grid: np.ndarray):
    size = grid.shape[0]
    grid, _ = measurements.label(grid.reshape((size, size)))
    grid = grid.flatten()

    top_bot = np.intersect1d(
        grid[:size],
        grid[grid.size - size :],
    )
    # Find cluster numbers on left and right
    left_right = np.intersect1d(
        grid[size - 1 :: size],
        grid[0::size],
    )
    # Remove empty sites
    top_bot = top_bot[top_bot != 0]
    left_right = left_right[left_right != 0]
    # Returns 1 if a cluster belongs on opposite edges, 0 otherwise
    return int(left_right.size > 0 or top_bot.size > 0)


def _sim_critical_point():
    """To find critical point WIP"""
    p_low = 0.0
    p_high = 1.0
    while abs(p_high - p_low) > 0.0001:
        p = (p_high + p_low) / 2
        grid = (np.random.rand(40000, 40000) < p).astype(np.int)
        is_infinite = _is_infinite(grid)
        if is_infinite:
            p_high = p
        else:
            p_low = p
        print(p_low, p_high)
    print(f"Critical Probability {(p_high+p_low)/2.0}")


def _sim_cluster_numbers():
    """To find number of clusters"""
    prob_list = np.linspace(0.0, 1.0, 500)
    numb_list = np.zeros_like(prob_list)
    for i in range(prob_list.size):
        grid = (np.random.rand(5000, 5000) < prob_list[i]).astype(np.int)
        _, n = measurements.label(grid)
        numb_list[i] = n
    plt.plot(prob_list, numb_list)
    # plt.plot(prob_list[1:], np.diff(numb_list))
    plt.show()


if __name__ == "__main__":
    # _sim_critical_point()
    _sim_cluster_numbers()
