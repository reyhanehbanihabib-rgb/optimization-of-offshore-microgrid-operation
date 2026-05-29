#!/usr/bin/env python
# coding: utf-8

# In[57]:


import numpy as np
import math
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d
from scipy.interpolate import CubicSpline
import scipy.integrate as integrate
from scipy.integrate import quad
import timeit
import inspect
import time
import os
from scipy.optimize import minimize
from scipy.optimize import differential_evolution
from scipy.optimize import basinhopping

from skopt import gp_minimize
from skopt.plots import plot_gaussian_process

from datetime import datetime
from random import seed
from random import random
# import warnings
# # warnings.filterwarnings('ignore')

import warnings
warnings.simplefilter('always')
import pandas as pd

import matplotlib.cm as cm
import matplotlib.pyplot as plt
from scipy import interpolate
# To plot pretty figures
import matplotlib as mpl
import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error

from random import randrange, uniform


mpl.rcParams.update(mpl.rcParamsDefault)
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]





pd.set_option("display.max_columns", None)





# To plot pretty figures

import matplotlib as mpl
import matplotlib.pyplot as plt


# #### Solver Tolerance

# In[80]:



tol_gamma = 1e-3
max_step_gamma = 50
tol_p = 10 # [Pa]

max_step_p = 50
tol_mdot = 1e-4
max_step_mdot = 50
tol_T = 0.01 #[K]
max_step_T = 50
tol_s = 0.1
max_step_s = 50
tol_h = 1 #[J/kg]
max_step_h = 50
tol_P = 0.1 # kW
max_step_P = 20


# Cycle Solver:
T_tol_recuperator = 3 # [degC], Tolerance for how much turbine outlet temperature can be calculated higher than it's value inlet to the recuperator hot side
max_step_p_cycle_solver = 20 # Maximum number of iterations to find the inlet mass flow that results in correct outlet pressure
tol_p_cycle_solver = 0.05e5 # [Pa]
max_step_T_7_cycle_solver = 15 # Maximum number of iterations to find the turbine outlet temperature in cycle solver



create_log = True


# #### Global Values

# In[307]:


# fuel components            [C        S       N       H       O       AR      HE]
M_fuel_gas =                 [12.01,   32.059, 14,     1.008,  16,     39.948, 4.003] # [g/mol], Fuel gas molecular weight
# Air components             [O2       N2      AR      SO2     CO2     H2O     HE] 
M_air_gas =                  [32,      28.013, 39.948, 64.063, 44.01,  18.015, 4.003] # [g/mol], Air gas molecular weight
wfr_dry_air =                [23.133,  75.553, 1.263,  0.000,  0.050,  0.000,  0.000] # [%], Dry air weight fraction
wfr_vapor   =                [0.000,   0.000,  0.000,  0.000,  0.000,  100.0,  0.000] # [%], Vapor air weight fraction



# Fuel composition          [C          S           N           H           O           Ar          He    ]
methane_fuel_composition  = [74.869,    00.000,     00.000,     25.131,     00.000,     00.000,     00.000]# Pure Methane
oil_fuel_composition      = [86.400,    00.200,     00.000,     13.400,     00.000,     00.000,     00.000]# Oil
hydrogen_fuel_composition = [00.000,    00.000,     00.000,     100.000,    00.000,     00.000,     00.000]# Pure Hydrogen



LHV_methane_nom = 48750 # [kJ/kg]
M_methane = 12.01 + 4 * 1.008; # [g/mol]
m_f_methane_nom = 0.007 # [kg/s]

LHV_hydrogen_nom = 120000 # [kJ/kg]
m_f_hydrogen_nom = 0.003 # [kg/s]
M_hydrogen = 2 * 1.008 # [g/mol]

h_ref = 0 # [J/kg. K]
s_ref = 0
# T_ref = 25 + 273.15 # [K]
T_ref = 0 + 273.15 # [K]
# T_ref_C = 25
T_ref_C = 0
# p_ref = 1e5 # [Pa]
p_ref = 0.1e5 # [Pa]

P_nom = 100 # kW
m_f_nom_methane = 8 # g/s
m_f_nom_hydrogen = 3 # g/s


# In[44]:


# Saturation table, T_vapor p_vapor
sat_vapor_table = np.array([[0.01, 611.3], [5, 872.1], [10, 1227.6], [15, 1705], [20, 2339], [25, 3169], [30, 4246], [35, 5628], [40, 7384], [45, 9593], [50, 12350], [55, 15758], [60, 19941], [65, 25030], [70, 31190], [75, 38580], [80, 47390]])


# In[45]:


# This function calculates static pressure, static temperature and Mach number of flow passing area A with known total propertoes and mass flow rate
def isentropic_flow(p, T, mdot, A, R, wfr_gas):
    density_stag = p / R / T
    V = mdot / density_stag / A
    M_temp = V / 1.4 / R / T
    M0 = M_temp
    M1 = 1.1 * M_temp  
    M_min = 1e-5
    M_max = 2
    e = tol_mdot
    N = max_step_mdot

    def error_fun(M):
        gamma, cp_coeff = gamma_flow(p, T, M, wfr_gas, R)
        error = mdot  - mdot_fun(p, T, M, A, gamma, R)
        error = np.array([error],dtype=float)
        return error, gamma, cp_coeff
    M, e_M, step_M, gamma, cp_coeff = secant_temp_3outputs(error_fun,M0,M1,e,N, M_min, M_max)
    cv = R / (gamma - 1)
    cp = R + cv
    ps = static_pressure(p, M, gamma)
    Ts = static_temperature(T, M, gamma)
    return ps, Ts, M, gamma, cp, cv, cp_coeff


# In[ ]:


def secant_temp_3outputs(f,x0,x1,e,N,x_min, x_max):
    x0 = float(x0)
    x1 = float(x1)
    e = float(e)
    N = int(N)
    step = 1
    condition = True
    
    while condition:
        min_value_flag = False
        max_value_flag = False   
        if step == 1:
            f_x0 = f(x0)
            f_x1 = f(x1)        
        if f_x0[0] == f_x1[0]:
            x2 = 0.5 * (x1 + x0)
            break
        x2 = x0 - (x1-x0)*f_x0[0]/( f_x1[0] - f_x0[0] ) 
    
        if x2 < x_min:
            x2 = x_min + x_min /100 * random()
            min_value_flag = True
        elif x2 > x_max:
            x2 = x_max - x_max /100 * random()
            max_value_flag = True

        f_x2 = f(x2)
        x0 = x1
        f_x0 = f_x1
        f_x1 = f_x2
        x1 = x2   



        step = step + 1
        
        if step > N:
            if min_value_flag:
                x2 = x_min
            elif max_value_flag:
                x2 = x_max
            else:
                x2 = x1
            break
        condition = abs(f_x2[0]) > e
    return x2, e, step, f_x2[1], f_x2[2]


# In[ ]:


def secant_temp_2outputs(f,x0,x1,e,N,x_min, x_max):
    x0 = float(x0)
    x1 = float(x1)
    e = float(e)
    N = int(N)
    step = 1
    condition = True
    
    while condition:
        min_value_flag = False
        max_value_flag = False   
        if step == 1:
            f_x0 = f(x0)
            f_x1 = f(x1)        
        if f_x0[0] == f_x1[0]:
            x2 = 0.5 * (x1 + x0)
            break
        x2 = x0 - (x1-x0)*f_x0[0]/( f_x1[0] - f_x0[0] ) 
    
        if x2 < x_min:
            x2 = x_min + x_min /100 * random()
            min_value_flag = True
        elif x2 > x_max:
            x2 = x_max - x_max /100 * random()
            max_value_flag = True

        f_x2 = f(x2)
        x0 = x1
        f_x0 = f_x1
        f_x1 = f_x2
        x1 = x2   



        step = step + 1
        
        if step > N:
            if min_value_flag:
                x2 = x_min
            elif max_value_flag:
                x2 = x_max
            else:
                x2 = x1
            break
        condition = abs(f_x2[0]) > e
    return x2, e, step, f_x2[1]


# In[ ]:


# This function calclates the value of gamma for flow with known total pressure and total temperature, Mach number and composition
def gamma_flow(p, T, M, wfr_gas, R):
    gamma0 = 1.2
    gamma1 = 1.3
    gamma_min = 1.00001
    gamma_max = 2
    e = tol_gamma
    N = max_step_gamma
    def err_fun_gamma(gamma):
        Ts = static_temperature(T, M, gamma)
        ps = static_pressure(p, M, gamma)
        cp, cp_coeff = cp_calculator_complex_gas_old(Ts, wfr_gas)
        cv = cp - R
        error = cp / cv - gamma
        error = np.array([error],dtype=float)
        return error, cp_coeff
    gamma, e_gamma, step_gamma, cp_coeff = secant_temp_2outputs(err_fun_gamma,gamma0,gamma1,e,N, gamma_min, gamma_max)
    return gamma, cp_coeff


# In[ ]:


def flow_properties_based_on_T_ps(T, ps, mdot, A, R, wfr_gas):
    p0 = 1.01 * ps
    p1 = 1.05 * ps  
    p_min = 10
    p_max = 10e5
    e = tol_p
    N = max_step_p
      
    def err_fun_p(p):
        ps_cal, _, M, _, _, _, _ = isentropic_flow(p, T, mdot, A, R, wfr_gas)
        error = ps  - ps_cal
        error = np.array([error],dtype=float)
        return error, M
    
    p, e_p, step_p, M = secant_temp_2outputs(err_fun_p,p0,p1,e,N, p_min, p_max)
    return p, M
    


# In[46]:


# This function calculates flow properties based on enthalpy difference
def flow_properties_based_on_enthalpy(delta_h, T_ref, cp_ref, p_out, mdot_out, x_f_out, area_out):
    T0 = T_ref + 10
    T1 = T_ref - 10
    T_min = 100
    T_max = 10000
    e = tol_T
    N = max_step_T
    def err_fun_T(T):
        _, _, _, _, _, _, _, cp_coeff_out, _ = flow_properties_calculator(p_out, T, mdot_out, x_f_out, area_out)
        error = delta_h - (enthalpy_calculator(cp_coeff_out, T) - enthalpy_calculator(cp_coeff_out, T_ref)) 
        error = np.array([error],dtype=float)
        return error
    return T_out
        
    


# In[ ]:


# This function calculates flow properties based on enthalpy difference
def T_based_on_enthalpy_old(h, p_out, mdot_out, x_f_out, area_out):
    cp_dummy = 1000
    T0 = h/cp_dummy
    T1 = T0 + 100
    T_min = 100
    T_max = 10000
    e = tol_h
    N = max_step_T
    def err_fun_T(T):
        _, _, _, _, _, _, _, cp_coeff_out, _ = flow_properties_calculator(p_out, T, mdot_out, x_f_out, area_out)
        error = h - enthalpy_calculator(cp_coeff_out, T) 
        error = np.array([error],dtype=float)
        return error
    T_out, e_T, step_T = secant_temp(err_fun_T,T0,T1,e,N, T_min, T_max)  
    return T_out
        


# In[ ]:


# This function calculates flow properties based on enthalpy difference
def T_based_on_enthalpy(h, mdot_out, cp_coeff_out, area_out):
    cp_dummy = 1000
    T0 = h/cp_dummy
    T1 = T0 + 100
    T_min = 100
    T_max = 10000
    e = tol_h
    N = max_step_T
    def err_fun_T(T):
        error = h - enthalpy_calculator(cp_coeff_out, T) 
        error = np.array([error],dtype=float)
        return error
    T_out, e_T, step_T = secant_temp(err_fun_T,T0,T1,e,N, T_min, T_max)  
    return T_out
        


# In[47]:





# In[115]:


def flow_properties_calculator (p, T, mdot, x_f, A):
    mdot_fuel = mdot * x_f
    mdot_air = mdot - mdot_fuel
    wfr_gas = weight_fraction_calculator(air_fuel_composition, mdot_air, mdot_fuel)
    R = R_calculator(wfr_gas)
    ps, Ts, M, gamma, cp, cv, cp_coeff = isentropic_flow(p, T, mdot, A, R, wfr_gas)
    return ps, Ts, M, cp, cv, gamma, R, cp_coeff, wfr_gas


# In[ ]:


def fuel_properties_calculator (p, T, mdot_fuel, fuel_molecular_composition):
    # Assuming stagniation and static properties are equal for fuel
    cp_methane = cp_calculator_p_T(cp_methane_coefs, cp_methane_intercept, cp_methane_poly, T, p)
#     cv_methane = cp_calculator_p_T(cv_methane_coefs, cv_methane_intercept, cv_methane_poly, T, p)
#     R_methane = cp_methane - cv_methane
    h_methane = enthalpy_calculator_p_T(cp_methane_coefs, cp_methane_intercept, cp_methane_poly, T, p)
    cp_hydrogen = cp_calculator_p_T(cp_hydrogen_coefs, cp_hydrogen_intercept, cp_hydrogen_poly, T, p)
#     cv_hydrogen = cp_calculator_p_T(cv_hydrogen_coefs, cv_hydrogen_intercept, cv_hydrogen_poly, T, p)
#     R_hydrogen = cp_hydrogen - cv_hydrogen
    h_hydrogen = enthalpy_calculator_p_T(cp_hydrogen_coefs, cv_hydrogen_intercept, cv_hydrogen_poly, T, p)
    h_fuel = 1/100 * (h_methane * fuel_molecular_composition[0] + h_hydrogen * fuel_molecular_composition[1])
    return h_fuel


# In[ ]:


def cp_calculator_p_T(cp_coeff, cp_intercept, poly, T, p):
    # p should be converted to bar and T is in K. cp is J/g K which is equal to kJ/kg K
    poly_variables = poly.fit_transform([[T, p/1e5]])
    cp = (np.matmul(cp_coeff, poly_variables[0]) + cp_intercept)        
    return cp    


# In[311]:


# def isentropic_process_temperature_calculator_old(Ts1, ps1, ps2, wfr):
#     T_ref = 298.15; p_ref = 1e5; s_ref = 0
#     s1 = s_calc_correlation(T_ref, Ts1, p_ref, ps1, s_ref, wfr)    
#     T0 = Ts1 * (ps2/ps1)**(1-1/1.4)
#     T1 = T0 - 10
#     T_min = 100
#     T_max = 10000
#     e = tol_s
#     N = max_step_s
#     N = 1000
#     def err_fun_T_isen(T):
#         T_ref = 298.15; p_ref = 1e5; s_ref = 0
#         s_T = s_calc_correlation(T_ref, T, p_ref, ps2, s_ref, wfr)    
#         error = s1 - (s_T)
#         error = np.array([error])
#         return error
#     Ts2, e_T, step_T = secant_temp(err_fun_T_isen,T0,T1,e,N, T_min, T_max)
#     return Ts2


# In[ ]:


def isentropic_process_temperature_calculator(Ts1, ps1, ps2, R, cp_coeff):
#     T_ref = 298.15; p_ref = 1e5; s_ref = 0
    T_ref = 273.15; p_ref = 0.1e5; s_ref = 0
    s1 = s_calc_correlation(T_ref, Ts1, p_ref, ps1, s_ref, R, cp_coeff)
    T0 = Ts1 * (ps2/ps1)**(1-1/1.4)
    T1 = T0 - 10
    T_min = 100
    T_max = 10000
    e = tol_s
    N = max_step_s
#     N = 1000
    def err_fun_T_isen(T):
        T_ref = 273.15; p_ref = 0.1e5; s_ref = 0
        s_T = s_calc_correlation(T_ref, T, p_ref, ps2, s_ref, R, cp_coeff)    
        error = s1 - (s_T)
        error = np.array([error],dtype=float)
        return error
    Ts2, e_T, step_T = secant_temp(err_fun_T_isen,T0,T1,e,N, T_min, T_max)
    return Ts2


# In[ ]:


# def isentropic_process_temperature_calculator(Ts1, ps1, ps2, R, cp_coeff):
#     T0 = Ts1 * (ps2/ps1)**(1-1/1.4)
#     T1 = T0 - 10
#     T_min = 100
#     T_max = 10000
#     e = tol_s
#     N = max_step_s
#     N = 100
#     def err_fun_T_isen(T):
#         s_ref = 0
#         s_T = s_calc_correlation(Ts1, T, ps1, ps2, s_ref, R, cp_coeff)    
#         error = s_ref - (s_T)
#         error = np.array([error])
#         return error
#     Ts2, e_T, step_T = secant_temp(err_fun_T_isen,T0,T1,e,N, T_min, T_max)
#     return Ts2


# In[50]:


def isentropic_process1(pr, gamma):
    tr = pr**(1-1/gamma)
    return tr


# In[51]:


def avg(a, b):
    return (a + b)/2


# In[ ]:


# def s_calc(Ts1, Ts2, ps1, ps2, wfr):
#     T_ref = 298.15; p_ref = 1e5; s_ref = 0 
# #          s_calc_correlation(Ts1, Ts2, ps1, ps2, s1, R, cp_coeff)
#     s1 = s_calc_correlation(T_ref, Ts1, p_ref, ps1, s_ref, wfr)
# #          s_calc_correlation(Ts1, Ts2, ps1, ps2, s1, R, cp_coeff)
#     s2 = s_calc_correlation(Ts1, Ts2, ps1, ps2, s1, wfr)
# #     s_calc_correlation(Ts1, Ts2, ps1, ps2, s1, R, cp_coeff)
#     return s2


# In[ ]:


def s_calc_correlation(Ts1, Ts2, ps1, ps2, s1, R, cp_coeff):
    pr = ps2 / ps1
    if pr > 0: 
        press_function =  R * np.log(pr) # right had side of entropy function relation
    else:
        press_function = R * np.log(1.001)
    integral_entropy_function = quad(entropy_function, Ts1, Ts2, args=(cp_coeff,))
    s2 = s1 + integral_entropy_function[0] - press_function
    return s2   

 


# In[ ]:


def p_calc_based_on_s_Ts(s, Ts, R, cp_coeff):
    T_ref = 273.15; p_ref = 0.1e5; s_ref = 1000
    ps0 = 1e5
    ps1 = 1.1e5
    ps_min = 10
    ps_max = 10e5
    e = tol_p
    N = max_step_p
    
    def err_fun_ps(ps):
        s_cal = s_calc_correlation(T_ref, Ts, p_ref, ps, s_ref, R, cp_coeff)
        error = s - s_cal
        error = np.array([error],dtype=float)
        return error
    ps, e_p, step_p = secant_temp(err_fun_ps,ps0,ps1,e,N, ps_min, ps_max)
    
    return ps
    
    


# In[ ]:


def s_calc_correlation_nes(Ts1, Ts2, ps1, ps2, s1, wfr):
    no_descritization = 1000
    R = R_calculator(wfr)
    
    delta_T_step = (Ts2 - Ts1) / no_descritization
    Ts_vec = np.arange(start=Ts1, stop=Ts2, step=delta_T_step)
    ds_T_vec = np.array([])
    for step_no in range(len(Ts_vec)-1):
        Ts_current_step = Ts_vec[step_no]
        Ts_next_step = Ts_vec[step_no+1]
        cp_step,_ = cp_calculator_complex_gas_old(Ts_current_step, wfr)
        ds_T = cp_step * np.log(Ts_next_step/Ts_current_step) 
        ds_T_vec = np.append(ds_T_vec, ds_T)
        
    pr = ps2 / ps1
    Tr = Ts2/Ts1
    if pr > 0: 
        press_function =  R * np.log(pr) # right had side of entropy function relation
    else:
        press_function = R * np.log(1.001)
    ds_T = np.sum(ds_T_vec)
    s2 = s1 + ds_T - press_function
    return s2           
 


# In[ ]:


# def entropy_function(T, wfr):
#     P('entering entropy_function:', T, wfr)
#     entropy_function_value = dh_calc(T,wfr)/T
# #     print('dh_calc(T,wfr)=' + str(dh_calc(T,wfr)))
# #     print('entropy_function_value = ' + str(entropy_function_value))
#     P('returning entropy_function:', entropy_function_value)
#     return entropy_function_value


# In[92]:


def entropy_function_old(T, wfr):
    cp,_ = cp_calculator_complex_gas_old(T, wfr)
    entropy_function_value = cp /T
    return entropy_function_value
    


# In[ ]:


def entropy_function(T, cp_coeff):
    cp = cp_calculator_complex_gas(T, cp_coeff)
    entropy_function_value = cp /T
    return entropy_function_value


# In[ ]:


def enthalpy_calculator(cp_coeff, T):
    T_C_in = T - 273.16
    def enthalpy(T_C):
        h = 1000 * (np.polyval(cp_coeff, T_C))
        return h
    I = quad(enthalpy, T_ref_C, T_C_in)
    II = I[0]
    
#     print('cp_coeff='+str(cp_coeff))
#     print('T='+str(T))
#     print('T_C_in='+str(T_C_in))
#     print('h='+str(II))
    return II


# In[ ]:


def cp_calculator_complex_gas(T, cp_coeff):
    T_C = T - 273.15;
    cp_mix = 1000 * (np.polyval(cp_coeff, T_C))
    return cp_mix


# In[ ]:


def cp_calculator_complex_gas_old(T, wfr_gas):
    T_C = T - 273.15;
    # Weight fraction of gas components (percentage)
    wfr_gas = 0.01 * np.array([wfr_gas[4], wfr_gas[5], wfr_gas[1], wfr_gas[2], wfr_gas[0], wfr_gas[3], wfr_gas[6]])

    # CO2 H2O N2 Ar O2 SO2 He
    #derivative of coefficient function
    a_ij = np.array([[-7.8181e-6, 2.4665e-2, 4.0212e1], [-2.1225e-6, 1.4976e-2, 3.1575e1], [-2.3167e-6, 8.7401e-3, 2.7548e1], [1e-07, -0.0002, 20.843], [-2.5360e-6, 8.91796e-3, 2.9581e1], [0, 0, 0], [0, 0, 0]])
    
    # The unit of coefficients is in J/mol.K and we have to convert them into
    # J/kg.K with molecular weight as bellow
    # Cp_i = Cp_i[J/molK]/M_i[g/mol]
    
    M_molec = np.array([[44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003], [44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003], [44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003]])
    a_ij=a_ij.T
    a_ij = np.divide(a_ij, M_molec)
    
    # Specific heat 
    # flue gas
    cp_coeff = np.matmul(a_ij , wfr_gas); 
    cp_mix = 1000 * ( np.polyval(cp_coeff, T_C))
    return cp_mix, cp_coeff


# In[ ]:


def cp_coeff_calculator(wfr_gas):
    # Weight fraction of gas components (percentage)
    wfr_gas = 0.01 * np.array([wfr_gas[4], wfr_gas[5], wfr_gas[1], wfr_gas[2], wfr_gas[0], wfr_gas[3], wfr_gas[6]])

    # CO2 H2O N2 Ar O2 SO2 He
    #derivative of coefficient function
    a_ij = np.array([[-7.8181e-6, 2.4665e-2, 4.0212e1], [-2.1225e-6, 1.4976e-2, 3.1575e1], [-2.3167e-6, 8.7401e-3, 2.7548e1], [1e-07, -0.0002, 20.843], [-2.5360e-6, 8.91796e-3, 2.9581e1], [0, 0, 0], [0, 0, 0]])
    
    # The unit of coefficients is in J/mol.K and we have to convert them into
    # J/kg.K with molecular weight as bellow
    # Cp_i = Cp_i[J/molK]/M_i[g/mol]
    
    M_molec = np.array([[44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003], [44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003], [44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003]])
    a_ij=a_ij.T
    a_ij = np.divide(a_ij, M_molec)
    
    # Specific heat 
    # flue gas
    cp_coeff = np.matmul(a_ij , wfr_gas); 
    return cp_coeff


# In[83]:


def dh_calc(T,wfr_gas):
    # % Calculation of specific heat of gas mixtures
    # % T is Temperature in Kelvin 
    # % wfr_gas is a vector containing the weight fraction of gas
    # % components (O2 N2 AR SO2 CO2 H2O HE respectively) in percentage.
    # % Example:
    # % T=1100;
    # % gas_comp_wgtper=[15.243 73.699 1.232 0 5.084 4.742 0];
    # % Cp_gas=Cp_calc(T,gas_comp_wgtper)   [kJ/kgK]

    # % Formulation based on KREISPR documents
    # % Cp_mix(T) = Sum(wgtper_i*Cp_i);   

    # % Weight fraction of gas components (percentage)

    wgtper_vector = np.array([wfr_gas[4], wfr_gas[5], wfr_gas[1], wfr_gas[2], wfr_gas[0], wfr_gas[3], wfr_gas[6]])

    # % CO2 H2O N2 Ar O2 SO2 He
    # %derivative of coefficient function
    a_ij = np.array([    [4.48810E-3, 1.8523E-2, 1.09679E-2, 5.20427E-3, 8.43033E-3, 3.5715E-3, 5.19412E-3],    [2*8.41441E-6, -2*1.36412E-6, -2*2.27924E-6, -2*7.68710E-16, 2*1.04245E-6, 2*5.71173E-6, 0],    [-3*4.51476E-9, 3*4.19462E-9, 3*3.50401E-9, 3*8.14599E-19, 3*6.6907E-10, -3*3.33891E-9, 0],    [4*1.35238E-12, -4*1.62628E-12, -4*1.66851E-12, -4*3.83330E-22, -4*5.33122E-13, 4*1.01854E-12, 0],    [-5*1.68436E-16, 5*2.12968E-16, 5*2.83657E-16, 5*6.5986E-26, 5*1.01807E-16, -5*1.24998E-16, 0],    [0, 0, 0, 0, 0, 0, 0]])

    # % Specific heat 
    # %% flue gas
    wgtper_vector = wgtper_vector.T
    dh_coef_gas = np.matmul(a_ij, wgtper_vector);
    # dh_coef_gas=dh_coef_gas(end:-1:1);
    dh_coef_gas = np.flip(dh_coef_gas, 0)

    dh = np.polyval(dh_coef_gas, T) 
    return dh





# In[1]:


# from scipy.interpolate import interp1d
# from scipy import arange, array, exp

def interpolator1d(xs, ys, x):
    
    if x > xs[0] and x < xs[-1]:
        # find nearest values
        x0, idx0 = find_nearest(xs, x)
        xs_copy = np.copy(xs)
        xs_copy[idx0] = 1e10
        x1, idx1 = find_nearest(xs_copy, x)
        y0 = ys[idx0]
        y1 = ys[idx1]        
        
        if y0 == y1:
            y = y0
        else:
            if x0 != x1:
                slope = (y1 - y0)/(x1 - x0)
                y = y0 + slope * (x - x0)
            else:
                y = 0.5 * (y0 + y1)

    elif x < xs[0]:
        dy_dx = slop_calculator(xs, ys)
        slope = dy_dx[0]
        y = ys[0] + (x - xs[0]) * slope
        solpe_dev = abs(abs(slope) - abs(np.mean(dy_dx)))/abs(np.mean(dy_dx))
        if solpe_dev > 2:
            y = ys[0]
#             print('bound value is used for extrapolation')        
    else: # x > xs[-1]:
        dy_dx = slop_calculator(xs, ys)
        slope = dy_dx[-1]
        y = ys[-1] + (x - xs[-1]) * slope        
        solpe_dev = abs(abs(slope) - abs(np.mean(dy_dx)))/abs(np.mean(dy_dx))
        if solpe_dev > 2:
            y = ys[-1]
#             print('bound value is used for extrapolation')
    return y


# In[57]:


def slop_calculator(x, y):
    dy_dx = np.array([])
    for point_no in range(len(x) - 1):
        if x[point_no+1] != x[point_no]: 
            dy_dx_point = (y[point_no+1] - y[point_no]) / (x[point_no+1] - x[point_no])
        else: 
            dy_dx_point = 1000
        dy_dx = np.append(dy_dx, dy_dx_point)
    dy_dx = np.append(dy_dx, dy_dx[-1])
    return (dy_dx)
    


# In[ ]:


def stagnation_properties_calculator(Ts, ps, mdot, area, R, cp_coeff):
    density = ps / R / Ts
    V = mdot / density / area
    cp = cp_calculator_complex_gas(Ts, cp_coeff)
    cv = cp - R
    gamma = cp / cv
    M = V / (math.sqrt(gamma * R * Ts))
    T = Ts * (1 + (gamma - 1)/2 * M**2)
    p = ps * (1 + (gamma - 1)/2 * M**2)**(gamma/(gamma-1))
    return p, T, M


# In[60]:


def isentropic_process(Ts_in, ps_in, p_out, mdot_out, R_in, cp_coeff_in, area_out):
    ps_out_min = 10
    ps_out_max = 10e5
    ps_out0 = 0.99 * p_out
    ps_out1 = 0.95 * p_out
    e = tol_p
    N = max_step_p  
    def err_fun_p_isen(ps_out):
        Ts_out_isen = isentropic_process_temperature_calculator(Ts_in, ps_in, ps_out, R_in, cp_coeff_in)
        R_out = R_in; cp_coeff_out = cp_coeff_in
        p_out_isen, T_out_isen, M_out_isen = stagnation_properties_calculator(Ts_out_isen, ps_out, mdot_out, area_out, R_out, cp_coeff_out)
        error = p_out_isen - p_out
        error = np.array([error],dtype=float)
        return error
    ps_out_isen, e_ps_out_isen, step_ps_out_isen = secant_temp(err_fun_p_isen,ps_out0,ps_out1,e,N,ps_out_min,ps_out_max)
    Ts_out_isen = isentropic_process_temperature_calculator(Ts_in, ps_in, ps_out_isen, R_in, cp_coeff_in)
    R_out = R_in; cp_coeff_out = cp_coeff_in
    p_out_isen, T_out_isen, M_out_isen = stagnation_properties_calculator(Ts_out_isen, ps_out_isen, mdot_out, area_out, R_out, cp_coeff_out)
    return p_out_isen, T_out_isen
        


# In[305]:





# In[300]:


def dh_calc(T,wfr_gas):

    # % Calculation of specific heat of gas mixtures
    # % T is Temperature in Kelvin 
    # % wfr_gas is a vector containing the weight fraction of gas
    # % components (O2 N2 AR SO2 CO2 H2O HE respectively) in percentage.
    # % Example:
    # % T=1100;
    # % gas_comp_wgtper=[15.243 73.699 1.232 0 5.084 4.742 0];
    # % Cp_gas=Cp_calc(T,gas_comp_wgtper)   [kJ/kgK]

    # % Formulation based on KREISPR documents
    # % Cp_mix(T) = Sum(wgtper_i*Cp_i);   

    # % Weight fraction of gas components (percentage)

    wgtper_vector = np.array([wfr_gas[4], wfr_gas[5], wfr_gas[1], wfr_gas[2], wfr_gas[0], wfr_gas[3], wfr_gas[6]])

    # % CO2 H2O N2 Ar O2 SO2 He
    # %derivative of coefficient function
    a_ij = np.array([    [4.48810E-3, 1.8523E-2, 1.09679E-2, 5.20427E-3, 8.43033E-3, 3.5715E-3, 5.19412E-3],    [2*8.41441E-6, -2*1.36412E-6, -2*2.27924E-6, -2*7.68710E-16, 2*1.04245E-6, 2*5.71173E-6, 0],    [-3*4.51476E-9, 3*4.19462E-9, 3*3.50401E-9, 3*8.14599E-19, 3*6.6907E-10, -3*3.33891E-9, 0],    [4*1.35238E-12, -4*1.62628E-12, -4*1.66851E-12, -4*3.83330E-22, -4*5.33122E-13, 4*1.01854E-12, 0],    [-5*1.68436E-16, 5*2.12968E-16, 5*2.83657E-16, 5*6.5986E-26, 5*1.01807E-16, -5*1.24998E-16, 0],    [0, 0, 0, 0, 0, 0, 0]])

    # % Specific heat 
    # %% flue gas
    wgtper_vector = wgtper_vector.T
    dh_coef_gas = np.matmul(a_ij, wgtper_vector);
    # dh_coef_gas=dh_coef_gas(end:-1:1);
    dh_coef_gas = np.flip(dh_coef_gas, 0)


    dh = np.polyval(dh_coef_gas, T) 

    return dh





# In[117]:


def enthalpy_calculator_p_T(cp_coeff, cp_intercept, poly, T, p):
    # this is only for fuel. cp comes in kJ/kgK, T is K and p should be changed from Pa to bar
    def cp_T(T):
        poly_variables = poly.fit_transform([[T, p/1e5]])
        cp = 1000 * (np.matmul(cp_coeff, poly_variables[0]) + cp_intercept) 
        return cp
    I = quad(cp_T, T_ref, T)
    return I[0]    


# In[ ]:





# In[59]:


# This function calculate static tempearure based on total temperature and Mach number
def static_temperature(T, M, gamma):
    Ts = T * 1/(1 + (gamma - 1)/2 * M**2)
    return Ts


# In[60]:


# This function calculate static pressure based on total pressure and Mach number
def static_pressure(p, M, gamma):
    ps = p * (1 + (gamma - 1)/2 * M**2)**((-gamma)/(gamma - 1))
    return ps


# In[61]:


# This function calculates the massflow passing through a known area with specific total properties
def mdot_fun(p, T, M, A, gamma, R):

    try:
        mdot  = A * p/math.sqrt(T*gamma*R) * M * (1 + (gamma-1)/2 * M**2)**-(gamma+1)/(2*(gamma-1))
    except:
        print(T,gamma,R)
        pass
        
    return mdot


# In[102]:


def secant(f,x0,x1,e,N):
    # Converting x0 and e to float
    x0 = float(x0)
    x1 = float(x1)
    e = float(e)

    # Converting N to integer
    N = int(N)
    step = 1
    condition = True
    
    while condition:
        if f(x0) == f(x1):
            break
        
        f_x0 = f(x0)
        f_x1 = f(x1)
        x2 = x0 - (x1-x0)*f_x0[0]/( f_x1[0] - f_x0[0] ) 
        x0 = x1
        x1 = x2
        step = step + 1
        
        if step > N:
            break
        condition = abs((f(x2))) > e
    return x2, e, step


# In[ ]:


def secant_multivariable(f,x0,x1,e,N,x_index):
    # Converting x0 and e to float
    x0 = float(x0)
    x1 = float(x1)
    e = float(e)

    # Converting N to integer
    N = int(N)
    x_index = int(x_index)
    step = 1
    condition = True
    
    while condition:
        f_x0 = f(x0)
        f_x1 = f(x1)        
        
        if f(x0) == f(x1):
            break
                
        x2 = x0 - (x1-x0)*f_x0[x_index]/( f_x1[x_index] - f_x0[x_index]) 
        x2 = x0 - (x1-x0)*f_x0[x_index]/( f_x1[x_index] - f_x0[x_index] ) 
        
        x0 = x1
        x1 = x2
        step = step + 1
        
        if step > N:
            break
        f_x2 = f(x2)
        condition = abs(f_x2[x_index]) > e
    return x2, e, step, f_x2


# In[ ]:


def secant1(f,x0,x1,e,N):
    # Converting x0 and e to float
    x0 = np.array(x0)
    x1 = np.array(x1)
    e = float(e)
    
    # Converting N to integer
    N = int(N)
    step = 1
    condition = True
    
    while condition:
        if f(*x0) == f(*x1):
            break
        
        f_x0 = f(*x0)
        f_x1 = f(*x1)
        
        x2 = x0 - (x1-x0)*f_x0[0]/( f_x1[0] - f_x0[0]) 
        x2 = x0 - (x1-x0)*f_x0[0]/( f_x1[0] - f_x0[0] ) 
        x0 = x1
        x1 = x2
        step = step + 1
        
        if step > N:
            break
        condition = abs((f(*x2))) > e
    return x2, e, step


# In[59]:


def secant_temp(f,x0,x1,e,N,x_min, x_max):
    x0 = float(x0)
    x1 = float(x1)
    e = float(e)
    N = int(N)
    step = 1
    condition = True
    
    while condition:
        min_value_flag = False
        max_value_flag = False   
        if step == 1:
            f_x0 = f(x0)
            f_x1 = f(x1)        
        if f_x0 == f_x1:
            x2 = 0.5 * (x1 + x0)
            break
        x2 = x0 - (x1-x0)*f_x0[0]/( f_x1[0] - f_x0[0] ) 
    
        if x2 < x_min:
            x2 = x_min + x_min /100 * random()
            min_value_flag = True
        elif x2 > x_max:
            x2 = x_max - x_max /100 * random()
            max_value_flag = True

        f_x2 = f(x2)
        x0 = x1
        f_x0 = f_x1
        f_x1 = f_x2
        x1 = x2   



        step = step + 1
        
        if step > N:
            if min_value_flag:
                x2 = x_min
            elif max_value_flag:
                x2 = x_max
            else:
                x2 = x1
            break
        condition = abs(f_x2) > e
    return x2, e, step


# In[ ]:


def secant_temp_1(f,x0,x1,e,N,x_min, x_max):
    x0 = float(x0)
    x1 = float(x1)
    e = float(e)
    N = int(N)
    step = 1
    condition = True
    while condition:
        min_value_flag = False
        max_value_flag = False   
        if step == 1:
            f_x0 = f(x0)
            f_x1 = f(x1) 
        if f_x0 == f_x1:
            x2 = 0.5 * (x1 + x0)
            break
        x2 = x0 - (x1-x0)*f_x0[0]/( f_x1[0] - f_x0[0] ) 
        if x2 < x_min:
            x2 = x_min + x_min /100 * random()
            min_value_flag = True
        elif x2 > x_max:
            x2 = x_max - x_max /100 * random()
            max_value_flag = True
        f_x2 = f(x2)
        x0 = x1
        f_x0 = f_x1
        f_x1 = f_x2
        x1 = x2   
        step = step + 1
        if step > N:
            if min_value_flag:
                x2 = x_min
            elif max_value_flag:
                x2 = x_max
            else:
                x2 = x1
            break
        condition = abs(f_x2) > e
    return x2, e, step


# In[1]:





# In[316]:


def flatten(a_list):
    new_array = np.array([])
    for i in range(len(a_list)):
        new_array = np.append(new_array, a_list[i])
    return new_array


# #### Components

# In[63]:


class Compressor():
    def __init__(self, omega_vec, beta_vec, mdot_TLU, eta_TLU, pr_TLU, eta_mech, area_A, area_B):
        self.omega_vec = omega_vec
        self.beta_vec = beta_vec
        self.mdot_TLU = mdot_TLU
        self.eta_TLU = eta_TLU
        self.pr_TLU = pr_TLU
        self.eta_mech = eta_mech
        self.area_A = area_A
        self.area_B = area_B
        
        
        


# In[64]:


class Turbine():
    def __init__(self, omega_vec, pr_vec, mdot_TLU, eta_TLU, eta_mech, area_A, area_B):
        self.omega_vec = omega_vec
        self.pr_vec = pr_vec
        self.mdot_TLU = mdot_TLU
        self.eta_TLU = eta_TLU
        self.eta_mech = eta_mech
        self.area_A = area_A
        self.area_B = area_B


# In[ ]:


class Diffuser():
    def __init__(self, Cp):
        self.Cp = Cp


# In[ ]:


# class Combustor():
#     def __init__(self, press_loss_coeff, eta_comb, area_A_air, area_A_fuel, area_B):
#         self.press_loss_coeff = press_loss_coeff
#         self.eta_comb = eta_comb
#         self.area_A_air = area_A_air
#         self.area_A_fuel = area_A_fuel
#         self.area_B = area_B
        


# In[ ]:


class Combustor():
    def __init__(self, AS, k_cc, eta, Q_loss_coeff, area_A_air, area_A_fuel, area_B):
        
        self.AS = AS
        self.k_cc = k_cc
        self.eta = eta
        self.Q_loss_coeff = Q_loss_coeff
        self.area_A_air = area_A_air
        self.area_A_fuel = area_A_fuel
        self.area_B = area_B


# In[ ]:


class Recuperator():
    def __init__(self, dp_coeff_cs, dp_coeff_hs, mdot_cs_design, eta_ht, area_A_cs, area_B_cs, area_A_hs, area_B_hs):
        self.dp_coeff_cs = dp_coeff_cs
        self.dp_coeff_hs = dp_coeff_hs
        self.mdot_cs_design = mdot_cs_design
        self.eta_ht = eta_ht
        self.area_A_cs = area_A_cs
        self.area_B_cs = area_B_cs
        self.area_A_hs = area_A_hs
        self.area_B_hs = area_B_hs


# In[ ]:


class Heat_Exchanger():
    def __init__(self, mdot_HE, dp_HE):
        self.mdot_HE = mdot_HE
        self.dp_HE = dp_HE
       


# In[ ]:


class Shaft():
    def __init__(self, shaft_loss_coeff, shaft_mech_eff):
        self.shaft_loss_coeff = shaft_loss_coeff
        self.shaft_mech_eff = shaft_mech_eff


# In[ ]:


class Components():
    def __init__(self, compressor, recuperator, turbine, diffuser, combustor, heat_exchanger, shaft):
        self.compressor = compressor
        self.recuperator = recuperator
        self.turbine = turbine
        self.diffuser = diffuser
        self.combustor = combustor
        self.heat_exchanger = heat_exchanger
        self.shaft = shaft


# In[ ]:


def heat_exchanger_decomposer(heat_exchanger_data):
    mdot_HE = heat_exchanger_data.mdot_HE
    dp_HE = heat_exchanger_data.dp_HE
    return mdot_HE, dp_HE
    


# In[ ]:


def diffuser_decomposer(diffuser_data):
    Cp = diffuser_data.Cp
    return Cp


# In[65]:


def compressor_decomposer(compressor_data, mdot_in, p_in, T_in, N):
    
    p_in = 1e-5 * p_in
    
    # component parameters extraction
    omega_vec = compressor_data.omega_vec
    beta_vec = compressor_data.beta_vec
    pr_TLU = compressor_data.pr_TLU
    mdot_TLU = compressor_data.mdot_TLU
    eta_TLU = compressor_data.eta_TLU
    eta_mech = compressor_data.eta_mech
    area_in = compressor_data.area_A
    area_out = compressor_data.area_B
    
    N_corr = N/(math.sqrt(T_in))
    mdot_corr = mdot_in * (math.sqrt(T_in)) / p_in 

    # finding mdot_corr data for the current N_corr
    mdot_current_N = np.array([])
    for col_no in range(len(beta_vec)):
        mdot_current_beta = mdot_TLU[:,col_no]
        mdot_N_beta = interpolator1d(omega_vec, mdot_current_beta, N_corr)
        mdot_current_N = np.append(mdot_current_N, mdot_N_beta, axis=None)
        
    # finding the value of beta
    beta = interpolator1d(mdot_current_N, beta_vec, mdot_corr)

    # finding pr
    pr_current_N = np.array([])
    for col_no in range(len(beta_vec)):
        pr_current_beta = pr_TLU[:,col_no]
        pr_N_beta = interpolator1d(omega_vec, pr_current_beta, N_corr)    
        pr_current_N = np.append(pr_current_N, pr_N_beta, axis=None)
    pr = interpolator1d(beta_vec, pr_current_N, beta)
    
    # finding eta
    eta_current_N = np.array([])
    for col_no in range(len(beta_vec)):
        eta_current_beta = eta_TLU[:,col_no]
        eta_N_beta = interpolator1d(omega_vec, eta_current_beta, N_corr)    
        eta_current_N = np.append(eta_current_N, eta_N_beta, axis=None)
    eta = interpolator1d(beta_vec, eta_current_N, beta)
   
    return  pr, eta, beta, area_in, area_out, eta_mech



# In[ ]:


def compressor_mass_flow_calculator(compressor_data, p_in, T_in, N):
    
    p_in = 1e-5 * p_in
    
    # component parameters extraction
    omega_vec = compressor_data.omega_vec
    beta_vec = compressor_data.beta_vec
    pr_TLU = compressor_data.pr_TLU
    mdot_TLU = compressor_data.mdot_TLU
    eta_TLU = compressor_data.eta_TLU
    eta_mech = compressor_data.eta_mech
    area_in = compressor_data.area_A
    area_out = compressor_data.area_B
    
    N_corr = N/(math.sqrt(T_in))
    
    # finding mdot_corr data for the current N_corr
    mdot_current_N = np.array([])
    for col_no in range(len(beta_vec)):
        mdot_current_beta = mdot_TLU[:,col_no]
        mdot_N_beta = interpolator1d(omega_vec, mdot_current_beta, N_corr)
        mdot_current_N = np.append(mdot_current_N, mdot_N_beta, axis=None)
        mdot_corr_min = np.amin(mdot_current_N)
        mdot_corr_max = np.amax(mdot_current_N)
        mdot_min = mdot_corr_min / ((math.sqrt(T_in)) / p_in)
        mdot_max = mdot_corr_max / ((math.sqrt(T_in)) / p_in)
    

    return  mdot_min, mdot_max



# In[66]:


def turbine_decomposer(turbine_data, mdot_in, p_in, T_in, N):
    
    p_in = 1e-5 * p_in
    
    # component parameters extraction
    omega_vec = turbine_data.omega_vec
    pr_vec = turbine_data.pr_vec
    mdot_TLU = turbine_data.mdot_TLU
    eta_TLU = turbine_data.eta_TLU
    eta_mech = turbine_data.eta_mech
    area_in = turbine_data.area_A
    area_out = turbine_data.area_B
    
    N_corr = N/(math.sqrt(T_in))
    mdot_corr = mdot_in * (math.sqrt(T_in)) / p_in 

    
    # finding mdot_corr data for the current N_corr
    mdot_current_N = np.array([])
    for col_no in range(len(pr_vec)):
        mdot_current_pr = mdot_TLU[:,col_no]
        mdot_N_pr = interpolator1d(omega_vec, mdot_current_pr, N_corr)
        mdot_current_N = np.append(mdot_current_N, mdot_N_pr, axis=None)
        
    # finding pr
    pr = interpolator1d(mdot_current_N, pr_vec, mdot_corr)
 
    # finding eta
    eta_current_N = np.array([])
    for col_no in range(len(pr_vec)):
        eta_current_pr = eta_TLU[:,col_no]
        eta_N_pr = interpolator1d(omega_vec, eta_current_pr, N_corr)
        eta_current_N = np.append(eta_current_N, eta_N_pr, axis=None)    
    eta = interpolator1d(pr_vec, eta_current_N, pr)
    return  pr, eta, area_in, area_out, eta_mech



# In[ ]:


# def combustor_decomposer(combustor_data):
        
#     # component parameters extraction
#     dp_coeff = combustor_data.press_loss_coeff
#     eta_comb = combustor_data.eta_comb
#     area_in_air = combustor_data.area_A_air
#     area_in_fuel = combustor_data.area_A_fuel
#     area_out = combustor_data.area_B
    

    
#     return  dp_coeff, eta_comb, area_in_air, area_in_fuel, area_out



# In[2]:


def combustor_decomposer(combustor_data):
        
    # component parameters extraction
    AS = combustor_data.AS
    k_cc = combustor_data.k_cc
    eta = combustor_data.eta
    Q_loss_coeff = combustor_data.Q_loss_coeff
    area_in_air = combustor_data.area_A_air
    area_in_fuel = combustor_data.area_A_fuel
    area_out = combustor_data.area_B        
    return  AS, k_cc, eta, Q_loss_coeff, area_in_air, area_in_fuel, area_out



# In[1]:


def recuperator_decomposer(recuperator_data):
        
    # component parameters extraction
    dp_coeff_cs = recuperator_data.dp_coeff_cs
    dp_coeff_hs = recuperator_data.dp_coeff_hs
    mdot_cs_design = recuperator_data.mdot_cs_design
    eta_ht = recuperator_data.eta_ht
    area_in_cs = recuperator_data.area_A_cs
    area_out_cs = recuperator_data.area_B_cs
    area_in_hs = recuperator_data.area_A_hs
    area_out_hs = recuperator_data.area_B_hs
    
    return  dp_coeff_cs, dp_coeff_hs, mdot_cs_design, eta_ht, area_in_cs, area_out_cs, area_in_hs, area_out_hs


# #### Maps

# In[67]:





# In[68]:





# In[ ]:





# In[ ]:





# In[69]:


def cp_calculator(T, wfr_gas):
    if gas_model == 'perfect':
        cp = 1000
        cp_coeff = [0,0,0]
    elif gas_model == 'air iseal gas':
        cp = 1000
        cp_coeff = [0,0,0]
    else: # gas model == 'combustion gas'
        cp = cp_calculator_complex_gas_old(T, wfr_gas)
    return cp
    
    
    
    


# In[315]:


# def cp_calculator_complex_gas(T, wfr_gas):
#     T_C = T - 273.15;
#     # Weight fraction of gas components (percentage)
#     wfr_gas = 0.01 * np.array([wfr_gas[4], wfr_gas[5], wfr_gas[1], wfr_gas[2], wfr_gas[0], wfr_gas[3], wfr_gas[6]])

#     # CO2 H2O N2 Ar O2 SO2 He
#     #derivative of coefficient function
#     a_ij = np.array([[-7.8181e-6, 2.4665e-2, 4.0212e1], [-2.1225e-6, 1.4976e-2, 3.1575e1], [-2.3167e-6, 8.7401e-3, 2.7548e1], [1e-07, -0.0002, 20.843], [-2.5360e-6, 8.91796e-3, 2.9581e1], [0, 0, 0], [0, 0, 0]])
    
#     # The unit of coefficients is in J/mol.K and we have to convert them into
#     # J/kg.K with molecular weight as bellow
#     # Cp_i = Cp_i[J/molK]/M_i[g/mol]
    
#     M_molec = np.array([[44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003], [44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003], [44.01, 18.015, 28.013, 39.948, 32, 64.063, 4.003]])
    
    
#     a_ij=a_ij.T
#     a_ij = np.divide(a_ij, M_molec)
#     wfr_gas = wfr_gas.reshape((len(wfr_gas), 1))
#     cp_coeff = np.matmul(a_ij , wfr_gas)
#     cp_mix = 1000 * ( np.polyval(cp_coeff, T_C))


#     return cp_mix, cp_coeff


# In[71]:


def R_calculator(wfr_gas):
    R_u = 8314.46 # Universal gas constant
    w_i = [a/b for a,b in zip(wfr_gas,M_air_gas)]
    w_i = 0.01 * np.array(w_i)
    M_m = 1 / sum(w_i)
    R = R_u / M_m # [J/kg.K]
    return R


# In[7]:


def weight_fraction_calculator(air_fuel_composition, mdot_air, mdot_fuel):

    mdot = mdot_air + mdot_fuel;
    
    fuel_fraction_C  = air_fuel_composition[0]
    fuel_fraction_S  = air_fuel_composition[1]
    fuel_fraction_N  = air_fuel_composition[2]
    fuel_fraction_H  = air_fuel_composition[3]
    fuel_fraction_O  = air_fuel_composition[4]
    fuel_fraction_Ar = air_fuel_composition[5]
    fuel_fraction_He = air_fuel_composition[6]
    air_fraction_O2  = air_fuel_composition[7]
    air_fraction_N2  = air_fuel_composition[8]
    air_fraction_Ar  = air_fuel_composition[9]
    air_fraction_SO2 = air_fuel_composition[10]
    air_fraction_CO2 = air_fuel_composition[11]
    air_fraction_H2O = air_fuel_composition[12]
    air_fraction_He  = air_fuel_composition[13]
    
    wfr_gas =     [(air_fraction_O2*mdot_air - fuel_fraction_S*mdot_fuel* M_air_gas[0]/ M_fuel_gas[1]- fuel_fraction_C*mdot_fuel* M_air_gas[0]/ M_fuel_gas[0] -0.5*fuel_fraction_H*mdot_fuel* M_air_gas[0]/(2* M_fuel_gas[3]))/mdot,    (air_fraction_N2*mdot_air + fuel_fraction_N*mdot_fuel)/mdot,    (air_fraction_Ar*mdot_air + fuel_fraction_Ar*mdot_fuel)/mdot,    (air_fraction_SO2*mdot_air + fuel_fraction_S*mdot_fuel*(1+ M_air_gas[0]/ M_fuel_gas[1]))/mdot,    (fuel_fraction_C*mdot_fuel*(1 +  M_air_gas[0]/ M_fuel_gas[0]) + air_fraction_CO2*mdot_air)/mdot,    (fuel_fraction_H*mdot_fuel*(1+0.5* M_air_gas[0]/(2* M_fuel_gas[3])) + air_fraction_H2O*mdot_air)/mdot,    (air_fraction_He*mdot_air + fuel_fraction_He*mdot_fuel)/mdot]

    if wfr_gas[0]<0:
        wfr_gas[0] = 0
        
    return wfr_gas


# In[73]:


def fuel_composition_calculator(methane_percentage, hydrogen_percentage):
    M_fuel = methane_percentage/100 * M_methane + hydrogen_percentage/100 * M_hydrogen;
    M_C = methane_percentage/100 * 12.01 / M_fuel;
    M_H = (methane_percentage/100 * 4 * 1.008 + hydrogen_percentage/100 * 2 * 1.008)/ M_fuel;

    # Fuel composition [C          S           N           H           O           Ar          Hr    ]
    fuel_wfr =         [100 * M_C, 0,          0,          100 * M_H,  0,          0,          0     ]
    LHV = (hydrogen_percentage * LHV_hydrogen_nom + methane_percentage * LHV_methane_nom)/100;
    m_fuel_nom = (hydrogen_percentage * m_f_hydrogen_nom + methane_percentage * m_f_methane_nom)/100; 

    return fuel_wfr, LHV, m_fuel_nom, M_fuel 


# In[74]:


# A fucntion to calculate molecular composition of humid air
# Tamb [K]
def air_composition_calculator(T_amb, p_amb, RH):
    T_amb = T_amb + 273.15
    p_amb = p_amb * 1e5
    T_v = sat_vapor_table[:,0] + 273.15 # vapor temperature vector
    p_v = sat_vapor_table[:,1] # vapor pressure vector
    cs = CubicSpline(T_v, p_v)
    press_sat = cs(T_amb)
    m_air_gas = 0.01 * np.matmul(M_air_gas, wfr_dry_air)
    m_vapor = 0.01 * np.matmul(M_air_gas, wfr_vapor)
    M_ratio = m_vapor / m_air_gas;
    phi_abs = M_ratio * press_sat * RH / 100 /(p_amb * 1e5 - press_sat * RH / 0.01) # Absolute humidity
    x_H2O = 100 * phi_abs / (1 + phi_abs) # water vapor weight fraction
    x_total = 1 + x_H2O /(100 - x_H2O) # total weight of humid air
    
    # calculation of weight fractions
    x_O2 = wfr_dry_air[0] / x_total
    x_N2 = wfr_dry_air[1] / x_total
    x_AR = wfr_dry_air[2] / x_total
    x_SO2 = wfr_dry_air[3] / x_total
    x_CO2 = wfr_dry_air[4] / x_total
    x_He = wfr_dry_air[6] / x_total

    # Resulting weight fraction
    air_wfr = [x_O2, x_N2, x_AR, x_SO2, x_CO2, x_H2O, x_He]

    return air_wfr


# In[28]:


def find_nearest(a, a0):
    a = np.array(a)
    #"Element in nd array `a` closest to the scalar value `a0`"
    idx = (np.abs(a - a0)).argmin()
    idx = (np.abs(a - a0)).argmin()
    return a.flat[idx], int(idx)


# In[298]:


def P(*arg):
    if print_log or create_log:
        frame = inspect.currentframe()
        frame = inspect.getouterframes(frame)[1]
        string = inspect.getframeinfo(frame[0]).code_context[0].strip()
        arguments = string[string.find('(') + 1:-1].split(',')

        A = arg
        names = []

        for i in range(len(arguments)):
            try:
                float(arguments[i])
                is_number = True
            except:
                is_number = False
            if is_number is not True:

                if type(A[i]) != str:

                    try:
                        names.append(str(arguments[i])+' = '+str(A[i]))
                    except:
                        names.append(str(arguments[i]))
                else:
                    names.append(arguments[i])
            else:
                names.append(arguments[i])

        if create_log and not print_log:

            with open('run log.txt', 'a') as f:
                B = len(names)
                for i in range(B):
                    if i > 0:
                        f.write(', ')                
                    f.write(names[i])
                f.write('\n')
                f.write('\n')
        if print_log and not create_log:
            print(','.join(names))   

        if print_log and create_log:
            print(','.join(names))   
            with open('run log.txt', 'a') as f:
                B = len(names)
                for i in range(B):
                    if i > 0:
                        f.write(', ')                
                    f.write(names[i])
                f.write('\n')
                f.write('\n') 
    else:
        pass
    return


# In[313]:


def Print(*arg):
    if print_key:
        frame = inspect.currentframe()
        frame = inspect.getouterframes(frame)[1]
        string = inspect.getframeinfo(frame[0]).code_context[0].strip()
        arguments = string[string.find('(') + 1:-1].split(',')

        A = arg
        names = []

        for i in range(len(arguments)):
            try:
                float(arguments[i])
                is_number = True
            except:
                is_number = False
            if is_number is not True:

                if type(A[i]) != str:

                    try:
                        names.append(str(arguments[i])+' = '+str(A[i]))
                    except:
                        names.append(str(arguments[i]))
                else:
                    names.append(arguments[i])
            else:
                names.append(arguments[i])

        print(','.join(names))    
    else:
        pass
    return


# In[144]:


# import inspect, re

# def varname(p):
#     for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
#         m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
#     if m:
#         return m.group(1)

# # if __name__ == '__main__':
# #     spam = 42
# #     print(varname(spam))


# In[2]:


def save_df(df, file_name, ext='.csv'):
    
    directory = os.getcwd()
    directory = directory.split('/')
    mother_directory = '/'
    for word in directory[0:-1]:
        if word != '':
            mother_directory = mother_directory + word + '/'

    save_table_path = mother_directory + 'Results/'
    save_table_path = save_table_path + 'Data Frames/'
    isExist = os.path.exists(save_table_path)
    if not isExist:
      # Create a new directory because it does not exist 
      os.makedirs(save_table_path)    
    if ext == '.csv':
        df.to_csv(save_table_path + file_name +'.csv')
    else:
        df.to_excel(save_table_path + file_name +'.xlsx')
    
    print('The data-frame is saved in: ' + save_table_path + file_name +'.csv')
    
    return

