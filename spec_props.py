# species data to share between files

# use the mass_prop function now, but kept for compatability
M_N2 = 28 # kg/kmol
M_N = 14 # kg/kmol
M_O2 = 32 # kg/kmol
M_O = 16 # kg/kmol
M_NO = 30 # kg/kmol
M_e = 5.486e-4 # kg/kmol

def species_masses():
    """return dictionary of species masses"""
    masses = {
        "N_2": 28,
        "N": 14,
        "O_2": 32,
        "O": 16,
        "NO": 30,
        "e": 5.486e-4
    }

    return masses

def blottner_data():
    """return data for blottner fits, see Table A.1 from scalabrins thesis
    """

    data = {
    "N_2":  {"A": 2.68e-02,   "B":  3.180e-01,    "C": -1.13e+01},
    "O_2":  {"A": 4.49e-02,   "B": -8.260e-02,    "C": -9.20e+00},
    "NO":   {"A": 4.36e-02,   "B": -3.360e-02,    "C": -9.58e+00},
    "N":    {"A": 1.16e-02,   "B":  6.033e-01,    "C": -1.24e+01},
    "O":    {"A": 2.03e-02,   "B":  4.290e-01,    "C": -1.16e+01},
    "NO+":  {"A": 3.02e-01,   "B": -3.5039791,    "C": -3.74e+00},
    "N_2+": {"A": 2.68e-02,   "B":  3.180e-01,    "C": -1.13e+01},
    "O_2+": {"A": 4.49e-02,   "B": -8.260e-02,    "C": -9.20e+00},
    "N+":   {"A": 1.16e-02,   "B": -6.030e-01,    "C": -1.24e+01},
    "O+":   {"A": 2.03e-02,   "B":  4.290e-01,    "C": -1.16e+01},
    "e":    {"A": 0,          "B":  0,            "C": -1.20e+01},
    }

    return data

def vhs_data(type):
    """returns VHS data for each species based on fits from january 2025 boyd update
    """
    # request d_ref or omega dictionary with input

    # d_ref values in Angstroms
    d_ref = {
        "N_2-N_2": 3.693,
        "N_2-O_2": 3.454,
        "N_2-NO": 3.668,
        "N_2-N": 3.391,
        "N_2-O": 3.080,
        "O_2-O_2": 3.549,
        "O_2-NO": 3.597,
        "O_2-N": 3.109,
        "O_2-O": 3.241,
        "NO-NO": 3.642,
        "NO-N": 3.281,
        "NO-O": 3.108,
        "N-N": 3.059,
        "N-O": 3.112,
        "O-O": 3.203,
    }

    # omega values
    omega = {
        "N_2-N_2": 0.679,
        "N_2-O_2": 0.716,
        "N_2-NO": 0.701,
        "N_2-N": 0.708,
        "N_2-O": 0.714,
        "O_2-O_2": 0.701,
        "O_2-NO": 0.705,
        "O_2-N": 0.716,
        "O_2-O": 0.729,
        "NO-NO": 0.707,
        "NO-N": 0.738,
        "NO-O": 0.715,
        "N-N": 0.737,
        "N-O": 0.742,
        "O-O": 0.791,
    }

    if type == "d_ref":
        return d_ref
    
    if type == "omega":
        return omega
    

def vss_data(type):
    """returns VHS data for each species based on fits from january 2025 boyd update
    """
    # request d_ref, alpha, or omega dictionary with input

    # d_ref values (in Angstroms)
    d_ref = {
        "N_2-N_2": 3.97,
        "N_2-O_2": 3.69,
        "N_2-NO": 4.04,
        "N_2-N": 3.72,
        "N_2-O": 3.29,
        "O_2-O_2": 3.79,
        "O_2-NO": 3.87,
        "O_2-N": 3.49,
        "O_2-O": 3.56,
        "NO-NO": 3.96,
        "NO-N": 3.73,
        "NO-O": 3.47,
        "N-N": 3.33,
        "N-O": 3.42,
        "O-O": 3.51,
    }

    # omega values
    omega = {
        "N_2-N_2": 0.679,
        "N_2-O_2": 0.719,
        "N_2-NO": 0.714,
        "N_2-N": 0.716,
        "N_2-O": 0.714,
        "O_2-O_2": 0.688,
        "O_2-NO": 0.698,
        "O_2-N": 0.726,
        "O_2-O": 0.737,
        "NO-NO": 0.707,
        "NO-N": 0.750,
        "NO-O": 0.723,
        "N-N": 0.737,
        "N-O": 0.741,
        "O-O": 0.781,
    }

    # alpha values
    alpha = {
        "N_2-N_2": 1.37,
        "N_2-O_2": 1.39,
        "N_2-NO": 1.40,
        "N_2-N": 1.46,
        "N_2-O": 1.37,
        "O_2-O_2": 1.39,
        "O_2-NO": 1.40,
        "O_2-N": 1.49,
        "O_2-O": 1.46,
        "NO-NO": 1.41,
        "NO-N": 1.54,
        "NO-O": 1.48,
        "N-N": 1.39,
        "N-O": 1.42,
        "O-O": 1.47,
    }

    if type == "d_ref":
        return d_ref
    
    if type == "omega":
        return omega
    
    if type == "alpha":
        return alpha
