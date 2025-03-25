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
        qc: convective heating rate, w/m^2
    """
    
    # lower velocity range
    if v >= 3000 and v <= 9500:
        const = 7.455e-9
        rho_exp = 0.4705
        v_exp = 3.089
        r_exp = -0.52

    # upper velocity range
    elif v > 9500 and v <= 17000:
        const = 1.27e-6
        rho_exp = 0.4678
        v_exp = 2.524
        r_exp = -0.52

    elif v < 3000 or v > 17000:
        # send error
        return 1e-10
        # raise ValueError('velocity out of range')

    return  100**2*const*rho**rho_exp*v**v_exp*rn**r_exp

def sg_conv_heating(rho, v, rn):
    """ brandis and johnston convective heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qc: convective heating rate in w/m^2
    """

    qc = 100**2*18.8*np.sqrt(rho/rn)*(v/1000)**3
    return qc
    

def bj_rad_heating(rho, v, rn):
    """ brandis and johnston radiative heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qr: radiative heating rate w/m^2
    """

    f_v = -53.26 + (6555)/(1 + (16000/v)**8.25)

    C = 3.416e4

    a_1 = 3.175e6*v**-1.8*rho**-0.1575
    if rn >= 0 and rn <= 0.5:
        amax = 0.61
    elif rn > 0.5 and rn <= 2.0:
        amax = 1.23
    elif rn > 2 and rn <= 10:
        amax = 0.49

    a = min(a_1, amax)
    b = 1.261

    return 100**2*C*rn**a*rho**b*f_v

def sg_rad_heating(rho, v, rn):
    """ sutton and graves radiative heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qr: radiative heating rate, w/m^2
    """
    # interpolate to find f(V)
    V_values = np.array([
        9000, 9250, 9500, 9750, 10000, 10250, 10500, 10750, 11000, 11500,
        12000, 12500, 13000, 13500, 14000, 14500, 15000, 15500, 16000
    ])
    f_values = np.array([
        1.5, 4.3, 9.7, 19.5, 35, 55, 81, 115, 151, 238,
        359, 495, 660, 850, 1065, 1313, 1550, 1780, 2040
    ])

    f_v = np.interp(v, V_values, f_values)
    C = 4.736e4
    a_1 = 1.072e6*v**-1.88*rho**-0.325
    if rn >= 0 and rn <= 1:
        amax = 1
    elif rn > 1 and rn <= 2.0:
        amax = 0.6
    elif rn > 2 and rn <= 3:
        amax = 0.5

    a = min(a_1, amax)
    b = 1.22

    return 100**2*C*rn**a*rho**b*f_v
