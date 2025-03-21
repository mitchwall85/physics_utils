import math
# https://www.grc.nasa.gov/www/k-12/airplane/normal.html
# generated with chatgpt, dutifully checked by me.

def normal_shock_m2(M1: float, gamma: float = 1.4) -> float:
    """
    Computes the downstream Mach number M2 for a normal shock.
    
    Parameters:
    -----------
    M1    : float
        Upstream Mach number
    gamma : float
        Ratio of specific heats (Cp/Cv), default is 1.4 for air
    
    Returns:
    --------
    M2 : float
        Downstream Mach number
    """
    numerator   = (gamma - 1)*M1**2 + 2
    denominator = 2*gamma*M1**2 - (gamma - 1)
    return math.sqrt(numerator/denominator)


def normal_shock_p2p1(M1: float, gamma: float = 1.4) -> float:
    """
    Computes the static pressure ratio P2/P1 across a normal shock.
    
    Parameters:
    -----------
    M1    : float
        Upstream Mach number
    gamma : float
        Ratio of specific heats
    
    Returns:
    --------
    p2p1 : float
        Pressure ratio P2/P1
    """
    return (2*gamma*M1**2 - (gamma - 1))/(gamma + 1)


def normal_shock_rho2rho1(M1: float, gamma: float = 1.4) -> float:
    """
    Computes the density ratio rho2/rho1 across a normal shock.
    
    Parameters:
    -----------
    M1    : float
        Upstream Mach number
    gamma : float
        Ratio of specific heats
    
    Returns:
    --------
    rho2rho1 : float
        Density ratio rho2/rho1
    """
    return ((gamma + 1.0)*M1**2) / ((gamma - 1.0)*M1**2 + 2.0)


def normal_shock_t2t1(M1: float, gamma: float = 1.4) -> float:
    """
    Computes the static temperature ratio T2/T1 across a normal shock.
    
    Parameters:
    -----------
    M1    : float
        Upstream Mach number
    gamma : float
        Ratio of specific heats
    
    Returns:
    --------
    t2t1 : float
        Temperature ratio T2/T1
    """
    p2p1 = normal_shock_p2p1(M1, gamma)
    rho2rho1 = normal_shock_rho2rho1(M1, gamma)
    return p2p1 / rho2rho1


def normal_shock_po2po1(M1: float, gamma: float = 1.4) -> float:
    """
    Computes the stagnation (total) pressure ratio P0_2/P0_1 across a normal shock.
    
    Parameters:
    -----------
    M1    : float
        Upstream Mach number
    gamma : float
        Ratio of specific heats
    
    Returns:
    --------
    po2po1 : float
        Stagnation pressure ratio P0_2/P0_1
    """
    top = ( (gamma + 1.0)*M1**2 ) / ( (gamma - 1.0)*M1**2 + 2.0 )
    bottom = ( (gamma + 1.0) / ( 2.0*gamma*M1**2 - (gamma - 1.0) ) )
    
    # Raise them to appropriate powers
    term1 = top**(gamma/(gamma - 1.0))
    term2 = bottom**(1.0/(gamma - 1.0))
    
    return term1 * term2


def normal_shock_all(M1: float, gamma: float = 1.4) -> dict:
    """
    Computes all key post-shock ratios and downstream Mach number for convenience.
    
    Parameters:
    -----------
    M1    : float
        Upstream Mach number
    gamma : float
        Ratio of specific heats

    Returns:
    --------
    results : dict
        Dictionary containing M2, P2/P1, rho2/rho1, T2/T1, and P0_2/P0_1
    """
    return {
        "M2":       normal_shock_m2(M1, gamma),
        "P2/P1":    normal_shock_p2p1(M1, gamma),
        "rho2/rho1":normal_shock_rho2rho1(M1, gamma),
        "T2/T1":    normal_shock_t2t1(M1, gamma),
        "P0_2/P0_1":normal_shock_po2po1(M1, gamma),
    }


if __name__ == "__main__":
    # Example usage
    M1_example = 2.0
    gamma_example = 1.4
    
    results = normal_shock_all(M1_example, gamma_example)
    print(f"Upstream Mach number (M1) = {M1_example}")
    for key, val in results.items():
        print(f"{key} = {val:.4f}")
