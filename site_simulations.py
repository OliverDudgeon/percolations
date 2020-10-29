"""Parallel processed version of H-K algorithm"""

import numpy as np
from multiprocessing import Pool
from scipy.ndimage import label
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def _gamma_exponent():
    N = 10000
    pc = 0.59274
    prob_list = np.linspace(0, 1.0, 100)
    cluster_mean = np.zeros_like(prob_list)
    try:
        cluster_mean = np.load("./site_data/clmean_data.npy")
    except FileNotFoundError:
        for i in range(prob_list.size):
            print(i)
            grid = np.random.rand(N, N) < prob_list[i]
            _, s = label(grid)
            cluster_mean[i] = np.sum(grid) / s
        np.save("./site_data/clmean_data.npy", cluster_mean)

    # prob_list -= pc
    plt.plot(prob_list, cluster_mean)
    # plt.plot(np.log(prob_list), np.log(cluster_mean))
    plt.show()


def _fisher_exponent():
    N = 35000
    grid = np.random.rand(N, N) < 0.59274
    labels, _ = label(grid)
    _, size = np.unique(labels, return_counts=True)
    size, counts = np.unique(size, return_counts=True)
    size = size[counts > N // 4]
    counts = counts[counts > N // 4] / np.sum(counts)

    def func(s, m, c):
        return m * s + c

    popt, pcov = curve_fit(func, np.log(size), np.log(counts))
    print(-popt[0])
    plt.plot(np.log(size), np.log(counts))
    plt.plot(np.log(size), func(np.log(size), *popt))
    plt.show()


def _beta_exponent():
    size = 20000
    pc = 0.59274
    prob_list = np.linspace(0.59274, 0.7, 300)
    frac_list = np.zeros_like(prob_list)
    try:
        frac_list = np.load("./site_data/order_data.npy")
    except FileNotFoundError:
        for i in range(prob_list.size):
            print(i)
            grid = np.random.rand(size, size) < prob_list[i]
            labels, _ = label(grid)
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

    popt, pact = curve_fit(func, np.log(prob_list), np.log(frac_list))

    plt.plot(prob_list, frac_list)
    plt.xlabel(r"|$p - p_{c}$|")
    plt.ylabel(r"P")
    plt.title(
        r"Order parameter vs site probability for 2d site percolation, $P\sim|p-p_{c}|^{\beta}$"
    )
    plt.legend(["Data"])

    plt.savefig("./site_data/order_fig.pdf", format="pdf")
    plt.savefig("./site_data/order_fig.svg", format="svg")
    plt.show()

    plt.plot(np.log(prob_list), np.log(frac_list))
    plt.plot(np.log(prob_list), func(np.log(prob_list), *popt))
    plt.xlabel(r"$\log |p-p_{c}|$")
    plt.ylabel(r"$\log P$")
    plt.title(
        f"Log-Log plot of order parameter vs site probability to find beta exponent $\\beta = {popt[0]}$"
    )
    plt.legend(["Data", "Linear Regression"])
    plt.show()


if __name__ == "__main__":
    _gamma_exponent()
    # _fisher_exponent()
    # _beta_exponent()
