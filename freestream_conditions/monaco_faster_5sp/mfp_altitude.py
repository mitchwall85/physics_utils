"""Calculate damkohler numbers for different reactions
"""
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as mcolors
from physics_utils.fluids.normal_shock import normal_shock_all
from physics_utils.fluids.fluids_utils import spec_heat_mix, mass_mol_mix
from physics_utils.spec_props import M_N2, M_O2, M_N, M_O
from physics_utils.constants import GASCON, BOLTZMANN, AVOGADRO
from physics_utils.freestream_conditions.monaco_faster_5sp.calc_inflow_mass_fun import calc_inflow_mass_5sp
from scipy.interpolate import griddata

def mu(m, t_ref, T, d, omega):
    mu_ref_O2 = (15*np.sqrt(np.pi*m*BOLTZMANN*t_ref))/(2*np.pi*d**2*(5 - 2*omega)*(7 - 2*omega))
    return mu_ref_O2*(T/t_ref)**omega

def mfp_N2(mu, rho, omega, m, T):
    return (2*(5 - 2*omega)*(7 - 2*omega))/(15)*np.sqrt(m/(2*np.pi*BOLTZMANN*T))*mu/rho

# Convert O2 mass from g/mol to kg for a single molecule
h_values  = np.linspace(0, 200, 200)

# vhs params: /home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/documents/vhs_vss_fits
omega_N2 = 0.663
d_N2 = 3.74e-10
m_N2_si = (M_N2/1000.0) / AVOGADRO
T_ref_N2 = 273.0

mfp_map = np.zeros(len(h_values))

for j, h in enumerate(h_values):

    freestream = calc_inflow_mass_5sp(h)
    cp = spec_heat_mix('cp', freestream[0], freestream[1:], [M_N2, M_O2, M_N, M_O], [2, 2, 1, 1]) 
    cv = spec_heat_mix('cv', freestream[0], freestream[1:], [M_N2, M_O2, M_N, M_O], [2, 2, 1, 1])   
    gamma = cp/cv
    n_tot = np.sum(freestream[1:])
    M_mix = mass_mol_mix(freestream[1:], [M_N2/1000, M_O2/1000, M_N/1000, M_O/1000])

    # free stream properties
    T_1 = freestream[0]
    n_tot = sum(freestream[1:])
    a_1 = np.sqrt(gamma * GASCON / M_mix * T_1)  # speed of sound


    # 3) Viscosity
    mu_N2 = mu(m_N2_si, T_ref_N2, T_1, d_N2, omega_N2)

    # 4) Density from n_O2
    #    If n_O2 is the number of molecules per m^3,
    #    then mass density = n_O2 * (mass per molecule).
    rho_O2 = n_tot * m_N2_si

    # 5) Mean free path
    mfp = mfp_N2(mu_N2, rho_O2, omega_N2, m_N2_si, T_1)

    mfp_map[j] = mfp

# plot mfp vs altitude
# make figure larger
plt.figure(figsize=(10, 8))
plt.plot(mfp_map, h_values)
plt.ylabel('Altitude (km)')
plt.xlabel('Mean Free Path (m)')
plt.title('Mean Free Path vs Altitude: 100% N2 with number density of real atmosphere')
plt.grid()
plt.xscale('log')
plt.xticks(np.logspace(-8, 3, 23))
plt.yticks(np.arange(0, 200, 5))



plt.savefig('mfp_vs_altitude.png')
