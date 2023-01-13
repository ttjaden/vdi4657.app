import numpy as np
import numpy_financial as npf
from scipy.optimize import curve_fit

# Internal fit function for invest costs
def invest_params_fit(x, a, b):
    return a * x**b

# Default parameters for invest costs
def invest_params_default():
    I_0 = 1375
    exp = -0.203
    return I_0, exp

# Parameters for invest costs function
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

# Function for invest costs
def invest_costs(capacity, I_0, exp):
    specific_invest_costs = I_0 * capacity^(exp) # €/kWh
    invest_costs = i * capacity         # €
    return specific_invest_costs, invest_costs

# cash flow for scenarios with increase of self-sufficiency
def cash_flow(invest_costs,
            feedin0,
            feedin,
            supply0,
            supply,
            tariff_feedin,
            tariff_supply,
            years,
            lifetime):
    # cash flow as list
    cashflow = []
    for y in range(1,years+1):
        # invest and reinvest
        if y == 1:
            invest = -1 * invest_costs
        elif y == lifetime+1:
            invest = -1 * (1-(lifetime/years)) * invest_costs
        else:
            invest = 0
        # residual value
        if y < years:
            residual_value = 0
        elif y == years and years < lifetime:
            residual_value = (1-(years/lifetime)) * invest_costs
        else:
            residual_value = 0
        # delta from grid supply and grid feedin
        delta_feedin = (feedin - feedin0) * tariff_feedin 
        delta_supply = -1 * (supply - supply0) * tariff_supply

        # cashflow array
        cashflow.append(invest+delta_feedin+delta_supply+residual_value)
    return cashflow

# Function for net present value (NPV)
def net_present_value(cashflow, interest_rate):
    NPV = npf.npv(interest_rate, cashflow)
    return NPV

# Function for internal rate of return (IRR)
def internal_rate_of_return(cashflow):
    IRR = npf.irr(cashflow)
    return IRR

# Function for amortisation time
def amortisation(cashflow):
    t_a = 0
    value = cashflow[0]
    for y in range(1, len(cashflow)):
        value = sum(cashflow[0:y+1])
        if value > 0 and t_a == 0:
            t_a = y+1
        else:
            pass
    return t_a

# Function for levelized cost of storage
def levelized_cost_of_storage(invest_costs,
                              feedin0,
                              feedin,
                              supply0,
                              supply,
                              tariff_feedin,
                              years,
                              lifetime,
                              interest_rate):
    costs=[]
    energy=[]
    for y in range(1,years+1):
        # invest and reinvest
        if y == 1:
            invest = invest_costs
        elif y == lifetime+1:
            invest = (1-(lifetime/years)) * invest_costs
        else:
            invest = 0
        # residual value
        if y < years:
            residual_value = 0
        elif y == years and years < lifetime:
            residual_value = (1-(years/lifetime)) * invest_costs
        else:
            residual_value = 0
        # delta from grid supply and grid feedin
        delta_feedin = (feedin0 - feedin) * tariff_feedin
        delta_supply = (supply0 - supply)

        # arrays
        costs.append((invest+residual_value+delta_feedin)/(1+interest_rate)**y)
        energy.append(delta_supply)
    
    LCOS = sum(costs)/sum(energy)
    return LCOS