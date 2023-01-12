import numpy as np
from scipy.optimize import curve_fit

def invest_params_fit(x, a, b):
    return a * x**b

def invest_params(xdata,ydata):
    # xdata = List with capacity
    # ydata = List with specific price
    bounds=(-1, [10000, 0])
    xdata = np.asarray(xdata)
    ydata = np.asarray(ydata)
    popt, pcov = curve_fit(invest_params_fit, xdata, ydata, bounds=bounds)
    I_0 = popt[0]
    exp = popt[1]
    return I_0, exp

# Default parameters for invest costs
def invest_params_default():
    I_0 = 1375
    exp = -0.203
    return I_0, exp

# Function for invest costs
def calc_invest(capacity, I_0, exp):
    i = I_0 * capacity^(exp)
    I = i * capacity
    return i, I

