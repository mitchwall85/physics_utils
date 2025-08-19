import numpy as np
from scipy.optimize import fsolve
from physics_utils.constants import AVOGADRO, GASCON, STEFBOLTZ, BOLTZMANN
from scipy.special import erf
import physics_utils.freestream_conditions.monaco_faster_5sp.calc_inflow_mass_fun as freestream_props
import physics_utils.fluids.fluids_utils as fluids
import physics_utils.spec_props as spec_props
import importlib

importlib.reload(freestream_props)
importlib.reload(fluids)


def bj_conv_heating(rho, v, rn, return_warnings=False):
    """ brandis and johnston convective heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qc: convective heating rate, w/m^2
    """

    if rho < 1e-5 or rho >5e-3:
        if return_warnings:
            print(f"density out of range, still returning value")
    
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
    

def bj_rad_heating(rho, v, rn, return_warnings=False, return_bad_value=False):
    """ brandis and johnston radiative heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qr: radiative heating rate w/m^2
    """

    # out of velocity range
    if v < 9500 or v > 17000:
        if return_warnings:
            print(f"velocity out of range, returning zero")
        if not return_bad_value:
            return 0
    
    if rho < 1e-5 or rho >5e-3:
        if return_warnings:
            print(f"density out of range, still returning value")
        if not return_bad_value:
            return 0

    f_v = -53.26 + (6555)/(1 + (16000/v)**8.25)

    C = 3.416e4

    a_1 = 3.175e6*v**-1.8*rho**-0.1575
    if rn >= 0 and rn <= 0.5:
        amax = 0.61
    elif rn > 0.5 and rn <= 2.0:
        amax = 1.23
    elif rn > 2 and rn <= 10:
        amax = 0.49
    else:
        print("nose radius out of range")

    a = min(a_1, amax)
    b = 1.261

    return 100**2*C*rn**a*rho**b*f_v

def sg_rad_heating(rho, v, rn, return_warnings=False):
    """ sutton and graves radiative heating correaltion

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m

    Returns:
        qr: radiative heating rate, w/m^2
    """

    # out of velocity range
    if v < 9000 or v > 16000:
        if return_warnings:
            print(f"velocity out of range, returning zero")
        return 0
    
    if rho < 6.66e-5 or rho >6.31e-4:
        if return_warnings:
            print(f"density out of range, still returning value")
        return 0


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

def bird_fm_heating(rho_inf, M_inf, rn, Ms, T, gamma, T_w):
    """cited in singh 2016, eqn 3.13

    Args:
        rho (_type_): _description_

    Returns:
        _type_: _description_

    """
    # I HAVE NOT TESTED ANY OF THIS YET
    """
    prefactor = rho_inf * (np.sqrt(2 * BOLTZMANN * T / Ms))**3 * (1 / (4 * np.sqrt(np.pi)))
    
    A = (gamma / 2) * M_inf**2
    B = gamma / (gamma - 1)
    C = ((gamma + 1) / (2 * (gamma - 1))) * (T_w / T_inf)
    
    exp_term = np.exp(- (gamma / 2) * M_inf**2)
    sqrt_pi_gamma_M = np.sqrt(np.pi * gamma / 2) * M_inf
    erf_term = erf(np.sqrt(np.pi * gamma / 2) * M_inf)
    
    bracket = (A + B - C) * exp_term \
              + sqrt_pi_gamma_M * (1 + erf_term) \
              - 0.5 * exp_term

    return prefactor * bracket

    """

def fm_simple_conv_heating(rho, v):
    """simplest free molecular heat flux

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s

    Returns:
        q_fm: free molecular heat flux, w/m^2
    """
    return 0.5*rho*v**3

def ss_conv_heating(v, rn, alpha, C_2, C_3, omega, freestream, labels):
    """Singh and schwartzentruber 2016 convective heating correlation, as a function of altitude.
    This does not do exactly the same thing as S&S:
        it assumes the simplest free molecular heat flux instead of the Bird one cited in the paper.

    Args:
        rho (float): freestream density, kg/m^3
        v (float): freestream velocity, m/s
        rn (float): nose radius, m
        ADD IN THE REST OF THE INPUTS

    Returns:
        qc: convective heating rate, w/m^2
    """

    # process inputs
    T = freestream[0]
    nDens = freestream[1:]
    list_spec = labels[1:] # trim T label
    
    # thermo props needed:
    # to find density of inflow, (part/m^3)*(mol/part)*(kg/mol) = n/nAvo*m
    mass = spec_props.species_masses() # mass dictionary data
    molar_masses = []
    for spec in list_spec:
        molar_masses.append(mass[spec]/1000)

    rho = fluids.mass_mix_kgm3(nDens, molar_masses)
    cv_mix = fluids.spec_heat_mix("cv", 0, nDens, molar_masses, [2, 2, 0, 0])
    cp_mix = fluids.spec_heat_mix("cp", 0, nDens, molar_masses, [2, 2, 0, 0])
    molar_mass_mix = fluids.mass_mol_mix(nDens, molar_masses)
    gam = cp_mix/cv_mix
    a = np.sqrt(gam*GASCON/molar_mass_mix*T)

    # mol fractions
    x_dict = fluids.ndens_to_mol_frac(nDens, list_spec)

    # viscosity of the freestream
    mu_inf = fluids.visc_wilkie_blottner(list_spec, x_dict, T)

    # rarefaction parameter:
    mach = v/a
    Re_inf = rho*v*rn/mu_inf
    W_r = mach**(2*omega)/Re_inf

    # free molecular heat flux to normalize things:
    q_fm= fm_simple_conv_heating(rho, v)
    h_fm = q_fm/q_fm

    q_bj = bj_conv_heating(rho, v, rn) # brandis and johnston convective heating
    h_ct = q_bj/q_fm/(1 - alpha*W_r) # heating coefficient with correction assumptions
    h_ss = h_ct + (h_fm - h_ct)*np.max([(W_r - C_2)/(W_r + C_3),0]) # blended heating coefficient
    q_ss = h_ss*q_fm # convective heating S&S

    return q_ss, W_r

