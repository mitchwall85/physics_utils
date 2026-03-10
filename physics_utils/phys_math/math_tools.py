import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import t

def autocorrelate(vect):
    """calculate autocorrelation of a vector

    Args:
        vect (numpy array): signal to calculate autocorrelation
    """
    
    signal = vect - np.mean(vect)

    length = np.size(signal)
    mean = np.mean(signal)
    #var_np = np.var(signal)

    var = 1/length*np.sum((signal-mean)**2)

    acf = np.zeros(np.size(signal))
    for i in np.arange(0, np.size(signal)):
        length = np.size(signal) - i
        acf_forward  = signal[i:-1]
        acf_backward = signal[0:-1-i]
        acf[i] = np.sum(acf_forward * acf_backward)/length

    acf = (acf - mean)/var

    return acf  

def fit_exponential(x_data, y_data, constraint=None):
    """fits an exponential function to data

    Args:
        x (np array): 
        y (np array): 

    Returns:
        _type_: _description_
    """
    if constraint is not None:
        x0 = constraint[0]
        y0 = constraint[1]

    # Define model with A eliminated using the constraint point
    def model(x, B):
        A = y0 * np.exp(B * x0)
        return A * np.exp(-B * x)

    # Fit only for B
    popt, _ = curve_fit(model, x_data, y_data, p0=(1.0,))
    B_fit = popt[0]
    A_fit = y0 * np.exp(B_fit * x0)

    # Return fitted curve
    return A_fit * np.exp(-B_fit * x_data)

def interp_x_at_y(x, y, y_target):
    """
    Interpolates to find x such that y(x) = y_target.
    Assumes x and y are 1D arrays and y is monotonic near the target.
    x and y are arrays, y_target is a float
    """
    x = np.asarray(x)
    y = np.asarray(y)

    if np.any(np.diff(y) < 0):
        # Ensure monotonicity isn't assumed unless specified
        sort_idx = np.argsort(y)
        x = x[sort_idx]
        y = y[sort_idx]

    if not (y.min() <= y_target <= y.max()):
        raise ValueError(f"y_target={y_target} is outside the range of y=[{y.min()}, {y.max()}]")

    return np.interp(y_target, y, x)


def confidence_interval(data, confidence):
    """
    Compute confidence intervals row-wise for an (n x m) array.

    Parameters:
    - data (np.ndarray): Array of shape (n_outputs, n_models)
    - confidence (float): Confidence level (default: 0.95)

    Returns:
    - ci_lower (np.ndarray): Lower bound of confidence interval (length n)
    - ci_upper (np.ndarray): Upper bound of confidence interval (length n)
    - means (np.ndarray): Mean of each row (length n)
    """
    n_models = data.shape[0]
    means = np.mean(data, axis=0)
    std_err = np.std(data, axis=0, ddof=1) / np.sqrt(n_models)
    t_multiplier = t.ppf((1 + confidence) / 2., df=n_models - 1)
    
    ci_half_width = t_multiplier * std_err
    ci_lower = means - ci_half_width
    ci_upper = means + ci_half_width
    
    return ci_lower, ci_upper, means

def percentile_confidence_interval(data, confidence=0.95):
    """
    Compute percentile-based confidence intervals (like MATLAB's prctile),
    row-wise for an (n_outputs x n_models) array.

    Parameters:
    - data (np.ndarray): Array of shape (n_outputs, n_models)
    - confidence (float): Confidence level (e.g., 0.95)

    Returns:
    - ci_lower (np.ndarray): Lower bound (percentile) for each row
    - ci_upper (np.ndarray): Upper bound (percentile) for each row
    """
    means = np.mean(data, axis=0)
    lower_pct = (1 - confidence) / 2 * 100
    upper_pct = (1 + confidence) / 2 * 100

    ci_lower = np.percentile(data, lower_pct, axis=0)
    ci_upper = np.percentile(data, upper_pct, axis=0)

    return ci_lower, ci_upper, means


