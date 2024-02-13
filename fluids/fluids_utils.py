import numpy as np
from scipy.optimize import fsolve


def find_rh_conds(u_1, rho_1, P_1, gam):

    def find_u2(u_2, u_1, rho_1, P_1, gam):
        gam = 1.4 # add this to inputs
        ans = -u_2 + u_1 + 2*gam/(gam-1)*(1/rho_1/u_1 + u_2**2/rho_1/u_1 - P_1*u_2/rho_1**2/u_1**2 - u_2/rho_1)
        return ans

    init_guess = 0.2*u_1
    freestream_conds = (u_1, rho_1, P_1, gam)
    u_2 = fsolve(find_u2, init_guess, freestream_conds)

    rho_2 = rho_1*u_1/u_2
    P_2 = -rho_2*u_2**2 + P_1 + rho_1*u_1**2

    return u_2, rho_2, P_2