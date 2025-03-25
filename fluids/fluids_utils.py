import numpy as np
from scipy.optimize import fsolve
from physics_utils.constants import AVOGADRO, GASCON, STEFBOLTZ
from physics_utils.spec_props import blottner_data, species_masses


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

def stef_bolts_qdot(eps, Tw):
    # get heat flux from stefan boltzmann law
    return eps*STEFBOLTZ*Tw**4

def stef_boltz_tw(eps, qdot):
    # get wall temp from stefan boltzmann law
    return (qdot/eps/STEFBOLTZ)**0.25

def mass_mix_kgm3(nDen, Ms):
    """average molar mass of a mixture

    Args:
        nDen (list): number densities of a species
        Ms (list): molar mass of each species

    Returns:
        float: mass of the mixture, kg/m^3
    """
    # average molar mass of a mixture
    M_tot = np.sum(np.multiply(nDen, Ms)/AVOGADRO)
    return M_tot


def mass_mol_mix(nDen, Ms):
    """average molar mass of a mixture

    Args:
        nDen (list): number densities of a species
        Ms (list): molar mass of each species

    Returns:
        float: mass of the mixture, kg/mol
    """
    # average molar mass of a mixture
    tot = np.sum(nDen)
    frac = nDen/tot
    M_tot = np.sum(frac*Ms)
    return M_tot

def blottner_fit(species, T):
    """return viscosity of a species using blottner fit

    Args:
        species (str): species name
        T (float): temperature, K

    Returns:
        float: viscosity, Pa-s
    """
    # get blottner data
    data = blottner_data()

    # calculate viscosity
    A = data[species]["A"]
    B = data[species]["B"]
    C = data[species]["C"]
    # eqn 2.27 from scalabrin
    mu_s = 0.1*np.exp((A*np.ln(T) + B)*np.ln(T) + C)
    return mu_s


def visc_wilkie_blottner(list_spec, x, T):
    """calculate viscosity using wilke's method

    Args:
        list_spec (list of strings): species in the mixture
        x (list of floats): molar fractions of each species in the list, adds to 1
        T (floats): temperature of mixture
    """

    mass = species_masses()

    def phi(list_spec, x, spec_s):

        mu_s = blottner_fit(spec_s, T)
        M_s = mass[spec_s]

        for spec_r in list_spec:

            mu_r = blottner_fit(spec_r, T)
            M_r = mass[spec_r]
            # eqn 2.26 from scalabrin
            numerator = (1 + np.sqrt(mu_s / mu_r) * (M_r / M_s)**(0.25))**2
            denominator = np.sqrt(8 * (1 + M_s / M_r))
            phi_s_r =  x * numerator / denominator

    s = 0
    for spec_s in list_spec:
        mu_s = blottner_fit(list_spec[s], T)
        phi_s = phi(list_spec, x, spec_s)

        mu += x[s]*mu_s/phi_s
        s += 1

    return mu




