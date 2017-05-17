__author__ = 'JosiahH'
import numpy as np
import sympy as sp
from scipy.optimize import newton_krylov
from copy import deepcopy
from trees import *

f_tol = 10**(-3)
r_u, r_d, r_uu, r_ud, r_dd, r_uuu, r_uud, r_udd, r_ddd, r_uuuu, r_uuud, r_uudd, r_uddd, r_dddd = \
    sp.symbols("r_u r_d r_uu r_ud r_dd r_uuu r_uud r_udd r_ddd r_uuuu r_uuud r_uudd r_uddd r_dddd", positive=True)

# bT = BDTTree('R', .1, up_value=r_u, down_value=r_d)
# bT.insert('H', up_value=r_uu, down_value=r_ud)
# bT.insert('T', up_value=r_ud, down_value=r_dd)
#
# bT.insert('HH', up_value=r_uuu, down_value=r_uud)
# bT.insert('HT', up_value=r_uud, down_value=r_udd)
# bT.insert('TH', up_value=r_uud, down_value=r_udd)
# bT.insert('TT', up_value=r_udd, down_value=r_ddd)
#
# bT.insert('HHH', up_value=r_uuuu, down_value=r_uuud)
# bT.insert('HHT', up_value=r_uuud, down_value=r_uudd)
# bT.insert('HTH', up_value=r_uuud, down_value=r_uudd)
# bT.insert('THH', up_value=r_uuud, down_value=r_uudd)
# bT.insert('HTT', up_value=r_uudd, down_value=r_uddd)
# bT.insert('THT', up_value=r_uudd, down_value=r_uddd)
# bT.insert('TTH', up_value=r_uudd, down_value=r_uddd)
# bT.insert('TTT', up_value=r_uddd, down_value=r_dddd)

# using new bdt_sympy function
bT = bdt_sympy(4, .1) # much simpler!

# print(bT.real_discount(2))
# bt_u = bT.up
# print(bt_u.depth())
# print(bt_u.real_discount(3))

def bdt(Yield, Volatility):
    """
    Assuming we have data for year 1 to n and probability of up or down is 1/2
    Only up to t = 5
    :param Yield: A list containing the yield rate
    :param Volatility: A list containing the yield volatility: must be the same length as Yield list.
    :return: a list containing calculated short rates
    """

    # let j be the year (starting from 0), j=1 corresponds to 2 in the table
    j = 1
    y, sig = Yield[j], Volatility[j]
    disc_val = bT.real_discount(1) # should be equal to 1/(1+yield)^2
    eqn1 = -(1/(1+y)**(j+1)) + disc_val
    eqn2 = -sig*2 + sp.log(r_u/r_d)

    j = 2
    y, sig = Yield[j], Volatility[j]
    # first equation of all
    disc_val = bT.real_discount(2)
    eqn3 = -(1/(1+y)**(j+1)) + disc_val
    # we know that rud is sqrt of the prod of ru and rd
    eqn4 = -r_ud + sp.sqrt(r_uu*r_dd)
    # we know what the log of the yield ratio must be
    bT_u = deepcopy(bT.find('H'))  # H subtree
    bT_d = deepcopy(bT.find('T'))  # T subtree
    yield_rates = [bT_u.real_discount(1)**(-1/2) - 1, bT_d.real_discount(1)**(-1/2) - 1] # should only have two elements
    eqn5 = -2*sig + sp.log(yield_rates[0]/yield_rates[1])

    j = 3
    y, sig = Yield[j], Volatility[j]
    disc_val = bT.real_discount(3)
    eqn6 = -(1/(1+y)**(j+1)) + disc_val
    eqn7 = -r_uud + sp.sqrt(r_uuu*r_udd)
    eqn8 = -r_udd + sp.sqrt(r_uud*r_ddd)
    # equations with yields: using bT_u and bT_d again, now discount 2 years
    yield_rates = [bT_u.real_discount(2)**(-1/3) - 1, bT_d.real_discount(2)**(-1/3) - 1]
    eqn9 = -2*sig + sp.log(yield_rates[0]/yield_rates[1])

    j = 4
    y, sig = Yield[j], Volatility[j] # y for yield, sig for volatility
    disc_val = bT.real_discount(4)
    eqn10 = -(1/(1+y)**(j+1)) + disc_val
    eqn11 = -r_uuud + sp.sqrt(r_uuuu*r_uudd)
    eqn12 = -r_uudd + sp.sqrt(r_uuud*r_uddd)
    eqn13 = -r_uddd + sp.sqrt(r_uudd*r_dddd)
    # bond values and yield
    yield_rates = [bT_u.real_discount(3) ** (-1 / 4) - 1, bT_d.real_discount(3) ** (-1 / 4) - 1]
    eqn14 = -2*sig + sp.log(yield_rates[0]/yield_rates[1])
    def fun(X):
        variables = [r_u, r_d, r_uu, r_ud, r_dd, r_uuu, r_uud, r_udd, r_ddd, r_uuuu, r_uuud, r_uudd, r_uddd, r_dddd]
        tuples = list(zip(variables, X))
        eqn1_val = np.array([float(np.abs(eqn1.subs(tuples)))])
        eqn2_val = np.array([float(np.abs(eqn2.subs(tuples)))])
        eqn3_val = np.array([float(np.abs(eqn3.subs(tuples)))])
        eqn4_val = np.array([float(np.abs(eqn4.subs(tuples)))])
        eqn5_val = np.array([float(np.abs(eqn5.subs(tuples)))])
        eqn6_val = np.array([float(np.abs(eqn6.subs(tuples)))])
        eqn7_val = np.array([float(np.abs(eqn7.subs(tuples)))])
        eqn8_val = np.array([float(np.abs(eqn8.subs(tuples)))])
        eqn9_val = np.array([float(np.abs(eqn9.subs(tuples)))])
        eqn10_val = np.array([float(np.abs(eqn10.subs(tuples)))])
        eqn11_val = np.array([float(np.abs(eqn11.subs(tuples)))])
        eqn12_val = np.array([float(np.abs(eqn12.subs(tuples)))])
        eqn13_val = np.array([float(np.abs(eqn13.subs(tuples)))])
        eqn14_val = np.array([float(np.abs(eqn14.subs(tuples)))])
        return np.hstack([eqn1_val, eqn2_val, eqn3_val, eqn4_val, eqn5_val, eqn6_val, eqn7_val, eqn8_val, eqn9_val,
                          eqn10_val, eqn11_val, eqn12_val, eqn13_val, eqn14_val])
    X_0 = [.01] * 14 # original guess: set a;; rates at initially known short rate
    # X_0 = [.14,.09,.19,.13,.09,.21,.16,.11,.08,.25,.19,.14,.11,.08] # guesses close to true values
    sol = newton_krylov(fun, X_0, f_tol=f_tol) # one can change the f_tol argument in newton_krylov for better results
    # sol = anderson(fun, X_0, f_tol=f_tol)
    rates_list = [.1]
    rates_list += list(sol)
    return rates_list

yields = [10/100, 11/100, 12/100, 12.5/100, 13/100]
volatility = [20/100, 19/100, 18/100, 17/100, 16/100]
true_vals = [10,14.32,9.79,19.42,13.77,9.76,21.79,16.06,11.83,8.72,25.53,19.48,14.86,11.34,8.65]
obtained = [100*x for x in bdt(yields, volatility)]
err = sum(list(map(lambda x,y:(x-y)**2,true_vals,obtained)))
print(obtained)
print(err/15)