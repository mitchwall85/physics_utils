# read in gram outputs and print out/calculate other relevant values
# this version plots things
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read results
results = pd.read_csv(f"faster_OUTPUT.csv")
Height_km = np.array(results.Height_km)
lat = np.array(results.Latitude_deg)
long = np.array(results.LongitudeE_deg)
temp = np.array(results.Temperature_K)
CO_mole_pct = np.array(results.COmole_pct)
Ar_mole_pct = np.array(results.Armole_pct)
CO_mole_pct = np.array(results.COmole_pct)
N2_mole_pct = np.array(results.N2mole_pct)
O2_mole_pct = np.array(results.O2mole_pct)
He_mole_pct = np.array(results.Hemole_pct)
H_mole_pct = np.array(results.Hmole_pct)
CH4_mole_pct = np.array(results.CH4mole_pct)
N_mole_pct = np.array(results.Nmole_pct)
O_mole_pct = np.array(results.Omole_pct)
O3_mole_pct = np.array(results.O3mole_pct)
N2O_mole_pct = np.array(results.N2Omole_pct)
H2O_mole_pct = np.array(results.H2Omole_pct)
total_nDensity = np.array(results.TotalNumberDensity_m3)

total_mole_pct = CO_mole_pct + Ar_mole_pct + N2_mole_pct + O2_mole_pct + He_mole_pct + H_mole_pct + CH4_mole_pct + N_mole_pct + O_mole_pct + O3_mole_pct + N2O_mole_pct + H2O_mole_pct

# plot all mole percentages with Height on the y axis, log scale on x axis
plt.figure()
plt.plot(CO_mole_pct, Height_km, label='CO')
plt.plot(Ar_mole_pct, Height_km, label='Ar')
plt.plot(N2_mole_pct, Height_km, label='N2')
plt.plot(O2_mole_pct, Height_km, label='O2')
plt.plot(He_mole_pct, Height_km, label='He')
plt.plot(H_mole_pct, Height_km, label='H')
plt.plot(CH4_mole_pct, Height_km, label='CH4')
plt.plot(N_mole_pct, Height_km, label='N')
plt.plot(O_mole_pct, Height_km, label='O')
plt.plot(O3_mole_pct, Height_km, label='O3')
plt.plot(N2O_mole_pct, Height_km, label='N2O')
plt.plot(H2O_mole_pct, Height_km, label='H2O')
plt.plot(total_mole_pct, Height_km, label='Total')
plt.xlabel('Mole %')
plt.ylabel('Height (km)')
plt.title('Mole Percentages vs Height')
plt.legend()
plt.grid()
#plt.xscale('log')
plt.savefig('mole_percentages_vs_height.png')


# recalcaulte mole percentages only include N2, O2, N, O proportinally scaling out the other species
total_mole_pct = N2_mole_pct + O2_mole_pct + N_mole_pct + O_mole_pct
N2_mole_pct = 100*(N2_mole_pct / total_mole_pct)
O2_mole_pct = 100*(O2_mole_pct / total_mole_pct)
N_mole_pct = 100*(N_mole_pct / total_mole_pct)
O_mole_pct = 100*(O_mole_pct / total_mole_pct)

# plot N2, O2, N, O mole percentages with Height on the y axis
plt.figure()
plt.plot(N2_mole_pct, Height_km, label='N2')
plt.plot(O2_mole_pct, Height_km, label='O2')
#plt.plot(N_mole_pct, Height_km, label='N')
plt.plot(O_mole_pct, Height_km, label='O')
plt.plot(O_mole_pct+N2_mole_pct+O2_mole_pct, Height_km, label='Total')
plt.xlabel('Mole %')
plt.ylabel('Height (km)')
plt.title('Mole Percentages vs Height')
plt.legend()
plt.grid()
#plt.xscale('log')
plt.savefig('mole_percentages_vs_height_reduced.png')