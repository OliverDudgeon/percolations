"""Parallel processed version of H-K algorithm"""

import numpy as np
from multiprocessing import Pool
from scipy.ndimage import label
from skimage import measure
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

pc = 0.59274


def _fisher_exponent():
    N = 40000
    grid = np.random.rand(N, N) < pc
    labels, _ = label(grid)
    _, size = np.unique(labels, return_counts=True)
    size, counts = np.unique(size, return_counts=True)
    size = size[counts > 2 * N]
    counts = counts[counts > 2 * N] / np.sum(counts)

    def func(s, m, c):
        return m * s + c

    popt, pcov = curve_fit(func, np.log(size), np.log(counts))
    print(-popt[0])
    plt.plot(np.log(size), np.log(counts))
    plt.plot(np.log(size), func(np.log(size), *popt))
    plt.show()


def _beta_exponent():
    size = 20000
    prob_list = np.linspace(pc, 0.7, 300)
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
    print(popt[0])
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


def _sim_critical_point():
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
            labels, _ = label(grid)
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
    plt.scatter(ns, ph_list)
    plt.scatter(ns, pl_list)
    plt.plot(ns, np.ones_like(ns) * p_c)
    plt.legend(["Critical probability", "Upper Probability", "Lower Probability"])
    plt.xlabel("Itteration number")
    plt.ylabel("Probability")
    plt.title(r"Plot of binary search for critical probability, $p_{c} = 0.5928$")
    plt.savefig("./site_data/critical_prob.pdf", format="pdf")
    plt.show()


if __name__ == "__main__":
    _sim_critical_point()
    # _fisher_exponent()
    # _beta_exponent()
