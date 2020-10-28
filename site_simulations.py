"""Parallel processed version of H-K algorithm"""

import numpy as np
from multiprocessing import Pool
from scipy.ndimage import measurements
import matplotlib.pyplot as plt


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
        print(i)
        grid = (np.random.rand(5000, 5000) < prob_list[i]).astype(np.int)
        _, n = measurements.label(grid)
        numb_list[i] = n
    plt.plot(prob_list, numb_list)
    # plt.plot(prob_list[1:], np.diff(numb_list))
    plt.show()


def _label_dot_counts():
    prob_list = np.linspace(0.0, 1.0, 500)
    numb_list = np.zeros_like(prob_list)
    try:
        numb_list = np.load("./site_data/ldc_data.npy")
    except FileNotFoundError:
        for i in range(prob_list.size):
            print(i)
            grid = (np.random.rand(5000, 5000) < prob_list[i]).astype(np.int)
            labels, _ = measurements.label(grid)
            label, sizes = np.unique(labels, return_counts=True)
            numb_list[i] = np.dot(label, sizes)
        np.save("./site_data/ldc_data.npy", numb_list)

    plt.plot(prob_list, numb_list)
    plt.xlabel("Site Probability")
    plt.ylabel("Sum of label numbers times cluster size")
    try:
        f = open("ldc_fig.svg")
        f.close()
    except FileNotFoundError:
        plt.savefig("./site_data/ldc_fig.svg", format="svg")
        plt.savefig("./site_data/ldc_fig.pdf", format="pdf")
    plt.show()


def _cluster_size_deviation():
    prob_list = np.linspace(0.0, 1.0, 500)
    numb_list = np.zer / os_like(prob_list)
    for i in range(prob_list.size):
        print(i)
        grid = (np.random.rand(5000, 5000) < prob_list[i]).astype(np.int)
        labels, _ = measurements.label(grid)
        _, sizes = np.unique(labels, return_counts=True)
        size, counts = np.unique(sizes, return_counts=True)
        numb_list[i] = np.dot(size ** 2, counts)
    plt.plot(prob_list, numb_list)
    plt.show()


if __name__ == "__main__":
    # _sim_critical_point()
    # _sim_cluster_numbers()
    _label_dot_counts()
