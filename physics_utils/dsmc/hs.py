""" functions for calculating stuff with the hard sphere model """
import numpy as np

def hs_mfp(n, d_avg):
    """hard sphere mean free path

    Args:
        n (float): number density in m^-3
        d_avg (float): avg reference diameter
    """
    return 1 / (np.sqrt(2) * np.pi * d_avg**2 * n)