import numpy as np

from physics_utils.freestream_conditions.monaco_faster_5sp.plot_mach_isocontours import (
    _altitude_knudsen_profile,
)


def test_altitude_knudsen_profile_uses_hard_sphere_mfp() -> None:
    data = {
        0.0: {
            0.0: {
                10.0: {"number density": 1.0e20},
                20.0: {"number density": 2.0e19},
            }
        }
    }

    d_avg_m = 3.7e-10
    l_ref_m = 0.5

    altitudes_km, kn_profile = _altitude_knudsen_profile(
        data=data,
        d_avg_m=d_avg_m,
        characteristic_length_m=l_ref_m,
        number_density_key="number density",
    )

    expected_lambda = 1.0 / (np.sqrt(2.0) * np.pi * d_avg_m**2 * np.array([1.0e20, 2.0e19]))
    expected_kn = expected_lambda / l_ref_m

    np.testing.assert_allclose(altitudes_km, np.array([10.0, 20.0]))
    np.testing.assert_allclose(kn_profile, expected_kn)
