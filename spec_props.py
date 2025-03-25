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