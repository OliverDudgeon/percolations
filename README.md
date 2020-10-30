# Percolations

Undergraduate fourth year physics mini-project by Oliver Dudgeon, Joseph Parker and Adam Shaw. For the Order Disorder and Fluctuations module at the University of Nottingham. We present two simulations: 

1. Site percolations on a 2D lattice with implementations of clustering algorithms and critical exponent calculations. 
2. Forest Fire model on a 2D lattice. Modelling fire spread through a lattice of trees. Calculating critical exponents. 

![Screenshot of the application](https://github.com/OliverDudgeon/percolations/blob/main/readmephoto.png)

# Steps to run

Python 3.7+ is required. We use `pygame` and `pygame_gui` for the user interface, `numpy` and `matplotlib` for numerical calculations and plotting. Once this repo is cloned to your desktop you may create a envionment based on ours using the provided `environment.yml` file:

```console
$ conda env create --file=environment.yml
```

Then activate it using

```console
$ conda activate physics37
```

Then inside this envionment run the main python script `percolation.py` with

```console
(physics37) $ python percolation.py
```
