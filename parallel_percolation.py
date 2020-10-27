"""Parallel processed version of H-K algorithm"""

import time
import numpy as np
from multiprocessing import Pool

GRID_SIZE = 5000


def _hoshen_kopelman(grid: np.ndarray):
    labels = np.ones(GRID_SIZE * GRID_SIZE // 2, dtype=np.int)

    def _find(old_label):
        """Loops through labels indexing them correctly"""
        new_label = old_label
        while (labels[new_label] != new_label).any():
            new_label = labels[new_label]
        while (labels[old_label] != old_label).any():
            label = labels[old_label]
            labels[old_label] = new_label
            old_label = label
        return new_label

    def _union(label1, label2):
        """Links to cluster together"""
        label = _find(label2)
        labels[_find(label1)] = label
        return label

    for i in range(GRID_SIZE * GRID_SIZE):
        if grid[i]:  # Loops through all the active sites
            row = i % GRID_SIZE
            column = i // GRID_SIZE

            # Cluster number of left site
            top = 0 if row == 0 else grid[i - 1]
            # Cluster number of top site
            left = 0 if column == 0 else grid[i - GRID_SIZE]

            # top = grid[i - 1]
            # # Cluster number of top site
            # left = grid[i - GRID_SIZE]
            # # Counts how many sites are next to it
            cluster = int(top > 0) + int(left > 0)
            if cluster == 0:  # If not in cluster, add to new one
                labels[0] += 1
                labels[int(labels[0])] = labels[0]
                grid[i] = labels[0]
            elif cluster == 1:
                # Next to one cluster so set to the cluster number
                # (one of left or top will be zero)
                grid[i] = max(top, left)
            elif cluster == 2:  # Next to two clusters
                grid[i] = _union(top, left)
    labels[labels[0]] = 0  # This is links emtyp cells to zero, makes them not drawn
    labels[0] = 0  # Stops infinite loop in find function
    grid = _find(grid)
    top_bot = np.intersect1d(
        grid[:GRID_SIZE],
        grid[grid.size - GRID_SIZE :],
    )
    # Find cluster numbers on left and right
    left_right = np.intersect1d(
        grid[GRID_SIZE - 1 :: GRID_SIZE],
        grid[0::GRID_SIZE],
    )
    # Remove empty sites
    top_bot = top_bot[top_bot != 0]
    left_right = left_right[left_right != 0]
    # Returns 1 if a cluster belongs on opposite edges, 0 otherwise

    return int(left_right.size > 0 or top_bot.size > 0)


def _sim_critical_point():
    """To find critical point WIP"""
    prob_list = np.linspace(0.59, 0.60, 10)
    count_list = np.zeros_like(prob_list)
    pool = Pool(12)
    start = time.time()
    for i in range(prob_list.size):
        print(i)
        args = [
            (np.random.rand(GRID_SIZE * GRID_SIZE) < prob_list[i]).astype(np.int)
            for _ in range(10)
        ]
        count_list[i] += sum(pool.map(_hoshen_kopelman, args))
    print(f"Time Elapsed {time.time() - start}")
    print(count_list)
    print(np.dot(prob_list, count_list) / (np.sum(count_list)))


if __name__ == "__main__":
    _sim_critical_point()
