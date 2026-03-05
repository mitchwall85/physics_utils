import numpy as np
from physics_utils.constants import STEFBOLTZ

def steph_boltz_temp(q, eps):
    """identify temperature for radiative equilibirum

    Args:
        q (float): incoming heat flux
    """
    return (q/eps/STEFBOLTZ)**.25
