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

    #print(f"for h: {height}, {interp_values}")

    return np.array(interp_values)


def calc_inflow_mass_5sp(height):
    """return freestream temperature and concetrations of 5sp air from EarthGram at a given height

    Args:
        height (float): altitude in km above sea level

    Returns:
        list: [temperature, N2 num density, O2 num density, N num density, O num density]
    """

    if height > 200 or height < 0:
        ValueError("Invalid altitude for this GRAM data.")

    file = r"/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/physics_utils/freestream_conditions/monaco_faster_5sp/conditions_gram_mass.txt"
    values = interp_specs(file, height)

    return values

    
