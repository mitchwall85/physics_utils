import numpy as np
from scipy.optimize import fsolve
from physics_utils.constants import AVOGADRO, GASCON, STEFBOLTZ


def bj_conv_heating(rho, v, rn):
    """ brandis and johnston convective heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qc: convective heating rate
    """
    
    # lower velocity range
    if v >= 3000 and v <= 9500:
        const = 7.455e-9
        rho_exp = 0.4705
        v_exp = 3.089
        r_exp = -0.52

    # upper velocity range
    elif v > 9500 and v <= 17000:
        const = 1.27e-9
        rho_exp = 0.4678
        v_exp = 2.524
        r_exp = -0.52

    if v < 3000 or v > 17000:
        # send error
        raise ValueError('velocity out of range')

    return  const*rho**rho_exp*v**v_exp*rn**r_exp

def bj_rad_heating(rho, v, rn):
    """ brandis and johnston radiative heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qr: radiative heating rate
    """

    def f(v):
        return -53.26 + (6555)/(1 + (16000/v)**8.25)

    C = 3.416e4

    a_1 = 3.175e6*v^-1.8*rho**-0.1575
    if rn <= 0 and rn <= 0.5:
        amax = 0.61
    elif rn > 0.5 and rn <= 2.0:
        amax = 1.23
    elif rn > 2 and rn <= 10:
        amax = 0.49

    a = max(0.1, a_1, amax)

    b = 1.261

    return C*rn**a*rho**b*f(v)