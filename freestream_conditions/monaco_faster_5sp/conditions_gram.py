# read in gram outputs and print out/calculate other relevant values
# this version plots things
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from physics_utils.constants import AVOGADRO_SI
from physics_utils.spec_props import m_N2, m_O2, m_O, m_N

# read results
results = pd.read_csv(f"faster_OUTPUT.csv")
Height_km = np.array(results.Height_km)
lat = np.array(results.Latitude_deg)
long = np.array(results.LongitudeE_deg)
temp = np.array(results.Temperature_K)

Ar_mass_pct = np.array(results.Armass_pct)
CO2_mass_pct = np.array(results.CO2mass_pct)
CO_mass_pct = np.array(results.COmass_pct)
N2_mass_pct = np.array(results.N2mass_pct)
O2_mass_pct = np.array(results.O2mass_pct)
He_mass_pct = np.array(results.Hemass_pct)
H_mass_pct = np.array(results.Hmass_pct)
CH4_mass_pct = np.array(results.CH4mass_pct)
N_mass_pct = np.array(results.Nmass_pct)
O_mass_pct = np.array(results.Omass_pct)
O3_mass_pct = np.array(results.O3mass_pct)
N2O_mass_pct = np.array(results.N2Omass_pct)
H2O_mass_pct = np.array(results.H2Omass_pct)
total_massDensity = np.array(results.Density_kgm3)

# recalcaulte mass percentages only include N2, O2, N, O proportinally scaling out the other species
total_mass_pct = N2_mass_pct + O2_mass_pct + N_mass_pct + O_mass_pct
N2_mass_pct = N2_mass_pct / total_mass_pct
O2_mass_pct = O2_mass_pct / total_mass_pct
N_mass_pct = N_mass_pct / total_mass_pct
O_mass_pct = O_mass_pct / total_mass_pct

# scale back inflow properties to number density as a proportion of the original total number density
print(f"avo: {AVOGADRO_SI}")
print(f"mN2: {m_N2}")
N2_nDensity = N2_mass_pct * total_massDensity / m_N2 * AVOGADRO_SI
O2_nDensity = O2_mass_pct * total_massDensity / m_O2 * AVOGADRO_SI
N_nDensity = N_mass_pct * total_massDensity / m_N * AVOGADRO_SI
O_nDensity = O_mass_pct * total_massDensity / m_O * AVOGADRO_SI

# print out a text file with rows: altitude, temperature, N2 density, O2 density, N density, O density
with open("conditions_gram_mass_v1.txt", "w") as f:
    f.write("Height_km, Temperature_K, N2_nDensity_m3, O2_nDensity_m3, N_nDensity_m3, O_nDensity_m3\n")
    for i in range(len(Height_km)):
        f.write(f"{Height_km[i]}, {temp[i]}, {N2_nDensity[i]}, {O2_nDensity[i]}, {N_nDensity[i]}, {O_nDensity[i]}\n")

