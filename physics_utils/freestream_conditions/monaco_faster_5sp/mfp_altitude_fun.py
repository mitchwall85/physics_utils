import numpy as np

from physics_utils.freestream_conditions.monaco_faster_5sp.calc_inflow_mass_fun import calc_inflow_mass_5sp
from physics_utils.spec_props import vhs_data
from physics_utils.dsmc.hs import hs_mfp



#def mfp_altitude_fun(alt):
def mfp_altitude_5sp_monaco(alt, output=False):
    file = "conditions_gram_mass.txt"
    values = calc_inflow_mass_5sp(alt, True) # temp, N2 nDensity, O2 nDensity, N nDensity, O nDensity

    # total number density
    n_tot = np.sum(values[0][1:])

    vhs_diams = vhs_data("d_ref")

    d_avg = 0
    for spec in values[1]:

        if f"{spec}-{spec}" in vhs_diams:
            spec_ind = values[1].index(spec)
            spec_n = values[0][spec_ind]
            spec_d_ref = vhs_diams[f"{spec}-{spec}"]*1e-10  # convert from nm to m
            d_avg += spec_d_ref*spec_n/n_tot

    mfp = hs_mfp(n_tot, d_avg)

    if output:
        print(f"Mean free path at altitude {alt} km: {mfp:.5e} m")

    return mfp


if __name__ == "__main__":
    alt = 100
    mfp_altitude_5sp_monaco(alt, True)
