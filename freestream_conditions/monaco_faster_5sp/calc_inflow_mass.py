import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

# function to open conditions_gram_v1.txt and interpolate the input height value to get the output values
def interp_specs(file_path, height):
    # Use numpy's genfromtxt to read the file and skip the header
    data = np.genfromtxt(file_path, delimiter=',', skip_header=1)

    interp_values = []

    for i in range(1, data.shape[1]):
        f = interp1d(data[:, 0], data[:, i], kind='linear')

        
        interp_values.append(f(height))

    print(f"for h: {height}, {interp_values}")

    return interp_values


file = "conditions_gram_mass_v1.txt"
height = 70 # km
values = interp_specs(file, height)

# write a file with the temperature, N2, O2, N, O densities at the given height
with open(f"conditions_gram_mass_v1_{height}.txt", "w") as f:
    f.write("Temperature_K, N2_nDensity_m3, O2_nDensity_m3, N_nDensity_m3, O_nDensity_m3\n")
    f.write(f"{values[0]:.5e}, {values[1]:.5e}, {values[2]:.5e}, {values[3]:.5e}, {values[4]:.5e}\n")

    