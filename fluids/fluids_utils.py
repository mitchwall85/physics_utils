import numpy as np
from scipy.optimize import fsolve
from physics_utils.constants import AVOGADRO, GASCON


def find_rh_conds(u_1, rho_1, P_1, gam):
    """this shit is probably broken rn"""

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

# specific heat functions
def cp(T, Ms, n_r_DOF):
    """cp for a single species
       assumed 3 translational dof and n_r_DOF rotational dof
       no vibrational or electronic dof yet assumed

    """
    Cv = 3/2*GASCON/Ms + 1/2*GASCON/Ms*n_r_DOF
    Cp = Cv + GASCON/Ms

    return  Cp # [J/kg-K]

def cv(T, Ms, n_r_DOF):
    """cv for a single species
       assumed 3 translational dof and n_r_DOF rotational dof
       no vibrational or electronic dof yet assumed

    """
    Cv_t = 3/2*GASCON/Ms
    Cv_r = 1/2*GASCON/Ms*n_r_DOF
    Cv = Cv_t + Cv_r

    return  Cv # [J/kg-K]


def spec_heat_mix(cp_or_cv, T, nDen, Ms, n_r_dof):
    """ caculate spec heat for a mixture.
    CURRENTLY NO TEMPERATURE DEPENDENCY"""

    c = []
    c_spec = 0
    # Cv for each species
    for i in np.arange(0, len(nDen)):
        if cp_or_cv == 'cv':
            c.append(cv(T, Ms[i], n_r_dof[i]))
        elif cp_or_cv == 'cp':
            c.append(cp(T, Ms[i], n_r_dof[i]))

    # total mass
    M_tot = np.sum(np.multiply(nDen, Ms)/AVOGADRO)

    # mixture fractions
    Y = []
    for i in np.arange(0, len(nDen)):
        Y.append(nDen[i]*Ms[i]/AVOGADRO/M_tot)

    # Cp for mixture
    for i in np.arange(0, len(nDen)):
        c_spec += Y[i]*c[i]

    return c_spec # [J/kg/K]