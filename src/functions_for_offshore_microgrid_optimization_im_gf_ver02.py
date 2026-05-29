#!/usr/bin/env python
# coding: utf-8
import numpy as np

import pandas as pd

import math
import os
from math import floor


# In[1]:


def Q_max_LM25PE (Power, TOT):
    Q_max = Power * Q_ref_LM25PE/P_ref_LM25PE
    return Q_max



def LM25PE (model_MGT, P_dem_LM25PE, T_amb, scaler=None):
    P_dem_MGT = P_dem_LM25PE/P_ref_LM25PE * P_ref_MGT
    MGT_predictions = nn_function(model_MGT, [P_dem_MGT,T_amb], scaler=scaler_MGT)   
    
    m_f_MGT, TOT_MGT, N_act_MGT, P_prod_MGT = MGT_predictions
    
    

        
    eff_MGT = P_dem_MGT/(LHV_NG*m_f_MGT)
    eff_LM25PE = eff_MGT + 0.078
    fuel_input_LM25PE = P_dem_LM25PE/eff_LM25PE # MW
    m_f_LM25PE = fuel_input_LM25PE/LHV_NG # kg/s
    TOT_LM25PE = (TOT_MGT+273.15)*(TOT_ref_LM25PE+273.15)/(TOT_ref_MGT+273.15) - 273.15 # degC
    
    if P_dem_LM25PE == 0:
        m_f_LM25PE = min_m_f_LM25PE_zero_load
        eff_LM25PE = 0    
        fuel_input_LM25PE = LHV_NG * m_f_LM25PE
        TOT_LM25PE =100
        
    return m_f_LM25PE, fuel_input_LM25PE, eff_LM25PE, TOT_LM25PE

def LM25PE_ (model_MGT, P_dem_LM25PE, T_amb, scaler=None):
    P_dem_MGT = P_dem_LM25PE/P_ref_LM25PE * P_ref_MGT
    
    
    
    pairs = [[x,y] for (x,y) in np.transpose(np.array([P_dem_MGT,T_amb])).tolist()]

    
    MGT_predictions = nn_function(model_MGT,pairs, scaler=scaler_MGT) 
    m_f_MGT=MGT_predictions[:,0]
    TOT_MGT=MGT_predictions[:,1]
    N_act_MGT=MGT_predictions[:,2]
    P_prod_MGT = MGT_predictions[:,3]
    eff_MGT = P_dem_MGT/(LHV_NG*m_f_MGT)
    eff_LM25PE = eff_MGT + 0.078
    fuel_input_LM25PE = P_dem_LM25PE/eff_LM25PE # MW
    m_f_LM25PE = fuel_input_LM25PE/LHV_NG # kg/s
    TOT_LM25PE = (TOT_MGT+273.15)*(TOT_ref_LM25PE+273.15)/(TOT_ref_MGT+273.15) - 273.15 # degC
      
    
    return m_f_LM25PE, fuel_input_LM25PE, eff_LM25PE, TOT_LM25PE

    
    
def LM25PE_MNT_cost(P_dem_LM25PE):
#     cost_LM25PE_MNT = -(maximum_maint_cost_hourly_LM25PE/P_ref_LM25PE**2)*(P_dem_LM25PE-P_ref_LM25PE)**2 + maximum_maint_cost_hourly_LM25PE
    cost_LM25PE_MNT = maximum_maint_cost_hourly_LM25PE * P_dem_LM25PE
    if cost_LM25PE_MNT < 0:
        cost_LM25PE_MNT = 0
    return cost_LM25PE_MNT

def LM25PE_MNT_cost_(P_dem_LM25PE):
#     cost_LM25PE_MNT = -(maximum_maint_cost_hourly_LM25PE/P_ref_LM25PE**2)*(P_dem_LM25PE-P_ref_LM25PE)**2 + maximum_maint_cost_hourly_LM25PE
    cost_LM25PE_MNT = maximum_maint_cost_hourly_LM25PE * P_dem_LM25PE
    cost_LM25PE_MNT[cost_LM25PE_MNT<0]=0
    

    return cost_LM25PE_MNT


def electrolyzer_prod(P_ELZ):
    no_ELZ_full = np.ceil(P_ELZ/max_power_ELZ)-1
    remaining_P_ELZ = P_ELZ - no_ELZ_full * max_power_ELZ
    
    H2_produced = no_ELZ_full * (f_ELZ(max_power_ELZ))* max_power_ELZ/LHV_H2 +  (f_ELZ(remaining_P_ELZ))* remaining_P_ELZ/LHV_H2
    
    
    
    
    return H2_produced


# In[3]:


from scipy.interpolate import interp1d

P_ = [0,1.00,1.60,2.33,2.94,3.79,4.40,5.01,5.74,6.59,7.08,7.70,8.18,8.92,9.89,10.62,11.60,12.70,13.79,14.64,15.74,16.96,18.05,19.51,20.97,22.43,24.51,25.36,26.82,28.04]      
NOx_ = [0,23.68,21.05,18.95,16.84,15.26,13.16,13.68,14.74,16.32,19.47,22.11,23.16,23.68,23.68,25.79,27.37,26.84,25.79,24.74,22.63,20.53,18.42,16.84,17.37,15.26,15.26,13.16,11.58,11.58]      
      
f_NOx = interp1d(P_, NOx_,bounds_error=False,fill_value="extrapolate",)



P_electrolyzer = [0.053571429,0.080357143,0.133928571,0.1875,0.214285714,0.241071429,0.254464286,0.308035714,0.361607143,0.401785714,0.46875,0.5625,0.736607143,0.924107143,1.098214286,1.299107143,1.513392857,1.700892857,1.915178571,2.183035714,2.410714286,2.638392857,2.90625,3.174107143,3.508928571,3.669642857,3.950892857,4.258928571,4.553571429,4.754464286,5.0625,5.290178571,5.53125,5.772321429,6.040178571,6.321428571,6.495535714,6.629464286]
eff_electrolyzer = [0,0.049689441,0.136645963,0.214285714,0.288819876,0.354037267,0.422360248,0.48136646,0.527950311,0.571428571,0.611801242,0.642857143,0.667701863,0.686335404,0.689440994,0.689440994,0.686335404,0.677018634,0.667701863,0.655279503,0.652173913,0.645962733,0.642857143,0.633540373,0.633540373,0.630434783,0.624223602,0.611801242,0.605590062,0.605590062,0.605590062,0.602484472,0.596273292,0.593167702,0.590062112,0.590062112,0.586956522,0.580745342]

f_ELZ = interp1d(P_electrolyzer, eff_electrolyzer, bounds_error=False,fill_value="extrapolate",)
max_power_ELZ=6


# In[4]:


def NOx_produced(P_LM25PE):

        

    mass_flow_exhaus = P_LM25PE/P_ref_LM25PE * mass_flow_exhaus_ref


#     NOx_prod_ppm = -0.0001*P_LM25PE**5 + 0.0078*P_LM25PE**4 - 0.2301*P_LM25PE**3 + 2.8819*P_LM25PE**2 - 13.83*P_LM25PE + 36.374
    NOx_prod_ppm = f_NOx(P_LM25PE)
    NOx_prod =  mass_flow_exhaus * NOx_prod_ppm * (M_NOx/M_Air)/10**6 # kg/s

    #     NOx_prod_cost = NOx_tax/10 * NOx_prod # EUR/s, 10 is to change NOK to EUR

    return NOx_prod


# In[9]:


LHV_NG = 52.2 # MJ/kg
LHV_H2 = 141.7 # MJ/kg 


P_ref_LM25PE = 22.9 # MW
Q_ref_LM25PE = 20 # MW
TOT_ref_LM25PE = 530 # degC
fuel_input_ref_LM25PE = 64.15 # MW
m_f_ref_LM25PE = 1.23 # kg/s
min_m_f_LM25PE_zero_load = 0.4


# P_min_acc_LM25PE = 0.5*P_ref_LM25PE # MW the power to be running
P_min_acc_LM25PE = 9
P_max_acc_LM25PE = P_ref_LM25PE # MW
Q_max_acc_LM25PE = Q_max_LM25PE (P_max_acc_LM25PE, TOT_ref_LM25PE) # MW


P_ref_MGT = 100 # kW
m_f_ref_MGT = 6.86 # g/s
TOT_ref_MGT = 645 # degC


max_P_GFA_to_GFB = 20 # MW
max_P_GFA_to_GFC = 20 # MW
# expense_power_imbalance = 100 # EUR/MW
expense_H2_imbalance = 100000 # EUR/kg/s
transfer_eff_P_GFA_to_GFB = (1-0.054)
transfer_eff_P_GFA_to_GFC = (1-0.11)


density_NG_at_STP = 0.716 # kg/m³
CO2_tax_per_Sm3 = 1.65 # NOK for 2022
CO2_tax = CO2_tax_per_Sm3 / density_NG_at_STP / 10 # EUR/kg


NOx_tax = 23.79 # NOK per kg for 2022
mass_flow_exhaus_ref = 90 # kg/s for baseload
M_NOx = 46 # gram per mole
M_Air = 28.96 #g/mole
NOx_emission_LM25PE = 15 #ppm


maximum_maint_cost_hourly_LM25PE = 0.70788 # from Hywind Tampen, project NPV calculation. With and without subsidies



max_allowed_power_deviation = 5
penalty_power_deviations = 10


# In[6]:


# Calculation of maximum FR given that LM 2500 can tolerate up to 75% H2 in volume basis

LHV_H2_per_m3 = 12.7 #MJ/M3
LHV_NG_per_m3 = 40.6 #MJ/M3

FR_min = 0.25*LHV_NG_per_m3/(0.25*LHV_NG_per_m3+0.75*LHV_H2_per_m3)


# In[26]:


CO2_tax


# In[ ]:


cost_NG_vec = []
cost_NG_tax_vec = []
cost_NOx_tax_vec = []
cost_MNT_GT_total_vec = []
cost_total_vec = []
penalty_H2_vec = []
penalty_P_imbalance_vec = []
penalty_total_vec = []

P_GFA_GT2_vec = []
P_GFA_GT3_vec = []
P_GFA_GT4_vec = []
P_GFC_GT1_vec = []
P_GFC_GT2_vec = []
P_GFC_GT3_vec = []

FR_GFA_GT1_vec = []
FR_GFA_GT2_vec = []
FR_GFA_GT3_vec = []
FR_GFA_GT4_vec = []
FR_GFC_GT1_vec = []
FR_GFC_GT2_vec = []
FR_GFC_GT3_vec = []        
P_WT_to_ELZ_vec = []
P_GFA_to_ELZ_vec = []
P_imbalance_GFA_vec = []
P_imbalance_GFB_vec = []
P_imbalance_GFC_vec = []

                             
P_GFA_to_GFB_vec = []
P_GFA_to_GFC_vec = []
P_GFB_from_GFA_vec = []
P_GFC_from_GFA_vec = []
P_GFA_from_GFC_vec = []
P_ELH_GFA_vec = []
P_ELH_GFB_vec = []
P_ELH_GFC_vec  = []
P_GFA_from_GFC_vec = []


P_GFA_from_GFC_vec = []    
H2_production_vec = []
H2_consumption_vec = []
m_NG_GFA_GT1_vec = []
m_H2_GFA_GT1_vec = []
m_NG_GFA_GT2_vec = []   
m_H2_GFA_GT2_vec = []  
m_NG_GFA_GT3_vec = [] 
m_H2_GFA_GT3_vec = []   
m_NG_GFA_GT4_vec = []
m_H2_GFA_GT4_vec = []   
m_NG_GFC_GT1_vec = []
m_H2_GFC_GT1_vec = []
m_NG_GFC_GT2_vec = []
m_H2_GFC_GT2_vec = []
m_NG_GFC_GT3_vec = []
m_H2_GFC_GT3_vec = []



eff_GFA_GT1_vec = []
eff_GFA_GT2_vec = []
eff_GFA_GT3_vec = []
eff_GFA_GT4_vec = []
eff_GFC_GT1_vec = []
eff_GFC_GT2_vec = []
eff_GFC_GT3_vec = []

H2_production_vec  = [] 
H2_consumption_vec  = []


P_GFA_GT1_dev_vec = []
P_GFA_GT2_dev_vec = []
P_GFA_GT3_dev_vec = []
P_GFA_GT4_dev_vec = []
P_GFC_GT1_dev_vec = []
P_GFC_GT2_dev_vec = []
P_GFC_GT3_dev_vec = []

P_imbalance_vec = []


# In[9]:



param_list = [
'cost_NG_vec',
'cost_NG_tax_vec',
'cost_NOx_tax_vec',    
'cost_MNT_GT_total_vec',
'cost_total_vec',
'penalty_H2_vec',
'penalty_P_imbalance_vec',
'penalty_total_vec',
'P_GFA_GT1_vec',
'P_GFA_GT2_vec',
'P_GFA_GT3_vec',
'P_GFA_GT4_vec',
'P_GFC_GT1_vec',
'P_GFC_GT2_vec',
'P_GFC_GT3_vec',
'FR_GFA_GT1_vec',
'FR_GFA_GT2_vec',
'FR_GFA_GT3_vec',
'FR_GFA_GT4_vec',
'FR_GFC_GT1_vec',
'FR_GFC_GT2_vec',
'FR_GFC_GT3_vec',       
'P_WT_to_ELZ_vec',
'P_GFA_to_ELZ_vec',
'P_imbalance_GFA_vec',
'P_imbalance_GFB_vec',
'P_imbalance_GFC_vec',
'P_GFA_to_GFB_vec',
'P_GFA_to_GFC_vec',
'P_GFB_from_GFA_vec',
'P_GFC_from_GFA_vec',
'P_GFA_from_GFC_vec',
'P_ELH_GFA_vec',
'P_ELH_GFB_vec',
'P_ELH_GFC_vec',
'P_GFA_from_GFC_vec',    
'H2_production_vec',
'H2_consumption_vec',
'm_NG_GFA_GT1_vec',   
'm_H2_GFA_GT1_vec',   
'm_NG_GFA_GT2_vec',   
'm_H2_GFA_GT2_vec',  
'm_NG_GFA_GT3_vec',   
'm_H2_GFA_GT3_vec',      
'm_NG_GFA_GT4_vec',   
'm_H2_GFA_GT4_vec',      
'm_NG_GFC_GT1_vec',   
'm_H2_GFC_GT1_vec',   
'm_NG_GFC_GT2_vec',   
'm_H2_GFC_GT2_vec',  
'm_NG_GFC_GT3_vec',   
'm_H2_GFC_GT3_vec',
'eff_GFA_GT1_vec',
'eff_GFA_GT2_vec',
'eff_GFA_GT3_vec',
'eff_GFA_GT4_vec',
'eff_GFC_GT1_vec',
'eff_GFC_GT2_vec',
'eff_GFC_GT3_vec',  
'P_GFA_GT1_dev_vec',
'P_GFA_GT2_dev_vec',
'P_GFA_GT3_dev_vec',
'P_GFA_GT4_dev_vec',
'P_GFC_GT1_dev_vec',
'P_GFC_GT2_dev_vec',
'P_GFC_GT3_dev_vec',
'P_imbalance_vec'
]


# In[11]:


# New version with optimizer defining the connections and platform powers are optimized by a table-based function

def MG_run(df_complete, x, parameter_definition, H2_tank_initial, x_band_statements, buy=True, sell=True):
    
    
    df_complete = df_complete.reset_index(drop=True)
    reserve_df = df_complete[['T_amb [degC]','P_dem_GFA [MW]','Q_dem_GFA [MW]','P_dem_GFB [MW]','Q_dem_GFB [MW]','P_dem_GFC [MW]','Q_dem_GFC [MW]','P_prod_WT [MW]']]
    
    # the NG price changes daily so it could be evaluated outside of the row loop
    
    Pr_NG = df_complete['NG_Price [EUR/MJ]'].iloc[0] #EUR/MJ
    Pr_NG_kg = Pr_NG*LHV_NG # EUR/kg
    reserve_df['NG_Price [EUR/kg]'] = Pr_NG_kg*np.ones(len(df_complete))    
    H2_available_vec = np.array([H2_tank_initial])
    H2_variation_vec = np.array([])
    
    delta_t = 60 * 60
    
    
    exec(parameter_definition)
    excess_power=[]
    for parameter_band_def in x_band_statements:
        exec(parameter_band_def)  
    
    # provide empty vectors
    for item in param_list:
        exp = item + '= set_zero_list("'+ item + '")'
        exec(exp,locals(),globals())
        

    for row in range(len(df_complete)):

        
# readings from the table
        T_amb = df_complete['T_amb [degC]'].iloc[row]
        P_dem_GFA = df_complete['P_dem_GFA-pred. [MW]'].iloc[row] #MW
        Q_dem_GFA = df_complete['Q_dem_GFA-pred. [MW]'].iloc[row] #MW
        P_dem_GFB = df_complete['P_dem_GFB-pred. [MW]'].iloc[row] #MW
        Q_dem_GFB = df_complete['Q_dem_GFB-pred. [MW]'].iloc[row] #MW        
        P_dem_GFC = df_complete['P_dem_GFC-pred. [MW]'].iloc[row] #MW
        Q_dem_GFC = df_complete['Q_dem_GFC-pred. [MW]'].iloc[row] #MW   
        P_WT = df_complete['P_prod_WT-pred. [MW]'].iloc[row] #MW
     
        
# evaluating the optimizing parameters
        if 'P_GFA_to_GFC_' in parameter_definition:
            min_P_GFA_to_GFC = eval('b_P_GFA_to_GFC_' + str(row) + '[0]')
            max_P_GFA_to_GFC = eval('b_P_GFA_to_GFC_' + str(row) + '[1]')
            P_GFA_to_GFC = eval('span_data_to_actual_data(P_GFA_to_GFC_' + str(row) + ', b_P_GFA_to_GFC_' + str(row) +')' )
        else:
            P_GFA_to_GFC = eval('b_P_GFA_to_GFC_' + str(row) + '[0]') # if the value is not set in X, then take the min value of the bound

        if 'P_GFA_to_ELZ_' in parameter_definition:
            min_P_GFA_to_ELZ = eval('b_P_GFA_to_ELZ_' + str(row) + '[0]')
            max_P_GFA_to_ELZ = eval('b_P_GFA_to_ELZ_' + str(row) + '[1]')
            P_GFA_to_ELZ = eval('span_data_to_actual_data(P_GFA_to_ELZ_' + str(row) + ', b_P_GFA_to_ELZ_' + str(row) +')' )
        else:
            P_GFA_to_ELZ_ = eval('b_P_GFA_to_ELZ_' + str(row) + '[0]') # if the value is not set in X, then take the min value of the bound

        if 'FR_GFA_GT1_' in parameter_definition:
            min_FR_GFA_GT1 = eval('b_FR_GFA_GT1_' + str(row) + '[0]')
            max_FR_GFA_GT1 = eval('b_FR_GFA_GT1_' + str(row) + '[1]')
            FR_GFA_GT1 = eval('span_data_to_actual_data(FR_GFA_GT1_' + str(row) + ', b_FR_GFA_GT1_' + str(row) +')' )
        else:
            FR_GFA_GT1 = eval('b_FR_GFA_GT1_' + str(row) + '[0]') # if the value is not set in X, then take the min value of the bound
            
            
        FR_GFA_GT2 = 1; FR_GFA_GT3 = 1; FR_GFA_GT4 = 1  
        FR_GFC_GT1=1;FR_GFC_GT2=1;FR_GFC_GT3=1
            
          
        
# Writting energy balances:
# Heat balance for GFB:
        Q_ELH_GFB = Q_dem_GFB
        P_ELH_GFB = Q_ELH_GFB/electrical_heater_eff
# Power balance for GFB:
        P_GFA_to_GFB = (P_dem_GFB + P_ELH_GFB)/transfer_eff_P_GFA_to_GFB
        P_GFB_from_GFA = P_GFA_to_GFB * transfer_eff_P_GFA_to_GFB
        if P_GFA_to_GFB > max_P_GFA_to_GFB:
            P_GFA_to_GFB = max_P_GFA_to_GFB
            print('Warning! the required power in GFB is not satidfied!')
        P_imbalance_GFB = 0
        P_loss_GFA_GFB_transmission = P_GFA_to_GFB*(1-transfer_eff_P_GFA_to_GFB)
        
        
        
# Heat balance for GFC:
        if P_GFA_to_GFC>=0: # the direction is from A to C
            P_GFC_from_GFA = P_GFA_to_GFC * transfer_eff_P_GFA_to_GFC
            P_GFA_from_GFC = 0
            P_dem_GFC_net = P_dem_GFC - P_GFC_from_GFA
            P_loss_GFA_GFC_transmission = P_GFA_to_GFC*(1-transfer_eff_P_GFA_to_GFC)
        else: # the direction is from C to A
            P_GFA_from_GFC = abs(P_GFA_to_GFC)
            P_GFC_from_GFA = 0
            P_dem_GFC_net = P_dem_GFC + abs(P_GFA_to_GFC)/transfer_eff_P_GFA_to_GFC
            P_loss_GFA_GFC_transmission = abs(P_GFA_to_GFC/transfer_eff_P_GFA_to_GFC - P_GFA_to_GFC)

        impossibility_cost_GFC, optimum_GFC = GFC_operation_Opt(T_amb,P_dem_GFC_net,Q_dem_GFC,FR_GFC_GT1,FR_GFC_GT2,FR_GFC_GT3,Pr_NG_kg,delta_t)
        P_GFC_GT1,P_GFC_GT2,P_GFC_GT3,P_GFC_GTs_total,P_ELH_GFC,        Q_max_GFC_GT1,Q_max_GFC_GT2,Q_max_GFC_GT3,Q_max_GFC_GTs_total,        fuel_input_GFC_GT1,fuel_input_GFC_GT2,fuel_input_GFC_GT3,        fuel_input_NG_GFC_GT1,fuel_input_H2_GFC_GT1,        fuel_input_NG_GFC_GT2,fuel_input_H2_GFC_GT2,        fuel_input_NG_GFC_GT3,fuel_input_H2_GFC_GT3,        m_f_NG_GFC_GT1,m_f_NG_GFC_GT2,m_f_NG_GFC_GT3,        m_f_H2_GFC_GT1,m_f_H2_GFC_GT2,m_f_H2_GFC_GT3,        m_f_NG_total_GFC,m_f_H2_total_GFC,        cost_NG_GFC,cost_NG_tax_GFC,cost_NOx_tax_GFC,cost_MNT_GT_total_GFC,cost_total_GFC = optimum_GFC
        P_imbalance_GFC = impossibility_cost_GFC
        P_imbalance_GFC = (P_GFC_GT1+P_GFC_GT2+P_GFC_GT3)-(P_dem_GFC_net+P_ELH_GFC)
        
# Heat balance for GFA:
        P_dem_GFA_net = P_dem_GFA + P_GFA_to_GFB + P_GFA_to_GFC + P_GFA_to_ELZ+                        -(abs(P_WT))
    
        impossibility_cost_GFA, optimum_GFA = GFA_operation_Opt(T_amb,P_dem_GFA_net,Q_dem_GFA,FR_GFA_GT1,FR_GFA_GT2,FR_GFA_GT3,FR_GFA_GT4,H2_available_vec[row],Pr_NG_kg,delta_t)
        P_GFA_GT1,P_GFA_GT2,P_GFA_GT3,P_GFA_GT4,P_GFA_GTs_total,P_ELH_GFA,        Q_max_GFA_GT1,Q_max_GFA_GT2,Q_max_GFA_GT3,Q_max_GFA_GT4,Q_max_GFA_GTs_total,        fuel_input_GFA_GT1,fuel_input_GFA_GT2,fuel_input_GFA_GT3,fuel_input_GFA_GT4,        fuel_input_NG_GFA_GT1,fuel_input_H2_GFA_GT1,        fuel_input_NG_GFA_GT2,fuel_input_H2_GFA_GT2,        fuel_input_NG_GFA_GT3,fuel_input_H2_GFA_GT3,        fuel_input_NG_GFA_GT4,fuel_input_H2_GFA_GT4,        m_f_NG_GFA_GT1,m_f_NG_GFA_GT2,m_f_NG_GFA_GT3,m_f_NG_GFA_GT4,        m_f_H2_GFA_GT1,m_f_H2_GFA_GT2,m_f_H2_GFA_GT3,m_f_H2_GFA_GT4,        m_f_NG_total_GFA,m_f_H2_total_GFA,        cost_NG_GFA,cost_NG_tax_GFA,cost_NOx_tax_GFA,cost_MNT_GT_total_GFA,cost_total_GFA = optimum_GFA
        P_imbalance_GFA = impossibility_cost_GFA        
        
        
        P_imbalance_GFA = (P_GFA_GT1+P_GFA_GT2+P_GFA_GT3+P_GFA_GT4+P_WT)-(P_dem_GFA+P_ELH_GFA+P_GFA_to_GFB+P_GFA_to_ELZ+P_GFA_to_GFC)
        
        
        eff_GFA_GT1 = P_GFA_GT1/fuel_input_GFA_GT1;
        eff_GFA_GT2 = P_GFA_GT2/fuel_input_GFA_GT2;
        eff_GFA_GT3 = P_GFA_GT3/fuel_input_GFA_GT3;
        eff_GFA_GT4 = P_GFA_GT4/fuel_input_GFA_GT4;
        eff_GFC_GT1 = P_GFC_GT1/fuel_input_GFC_GT1;
        eff_GFC_GT2 = P_GFC_GT2/fuel_input_GFC_GT2;
        eff_GFC_GT3 = P_GFC_GT3/fuel_input_GFC_GT3;        
        

# Calculation of all the power provided to the electrolyzer
        P_ELZ = P_GFA_to_ELZ
#         H2_produced = electrolyzer_efficiency * P_ELZ/LHV_H2
        H2_produced = electrolyzer_prod(P_ELZ)
        if H2_produced < 0:
            H2_produced = 0
        
        
        H2_production = H2_produced
# Cost calculation:
        cost_MNT_GT_total = cost_MNT_GT_total_GFA + cost_MNT_GT_total_GFC
        m_f_NG_total = m_f_NG_total_GFA + m_f_NG_total_GFC
        cost_NG = cost_NG_GFA + cost_NG_GFC
        cost_NG_tax = cost_NG_tax_GFA + cost_NG_tax_GFC
        cost_NOx_tax = cost_NOx_tax_GFA + cost_NOx_tax_GFC
        
        m_f_H2_total = m_f_H2_total_GFA + m_f_H2_total_GFC
        H2_consumption = m_f_H2_total
        H2_variation_vec = np.append(H2_variation_vec,H2_produced-m_f_H2_total)
        if row <len(df_complete)-1:
            H2_available_vec = np.append(H2_available_vec,H2_available_vec[0] + np.array(H2_variation_vec).sum())
       
        if H2_available_vec[row]-m_f_H2_total< 0:
            penalty_H2 = expense_H2_imbalance * abs(H2_available_vec[row]-m_f_H2_total)
        else: 
            penalty_H2 = 0


        
        penalty_P_imbalance = impossibility_cost_GFA + impossibility_cost_GFC
        
        
        P_GFA_GT1_dev = np.std(P_GFA_GT1_vec);# P_GFA_GT1_dev=0 if math.isnan(P_GFA_GT1_dev) else None
        P_GFA_GT2_dev = np.std(P_GFA_GT2_vec);# P_GFA_GT2_dev=0 if math.isnan(P_GFA_GT2_dev) else None
        P_GFA_GT3_dev = np.std(P_GFA_GT3_vec);# P_GFA_GT3_dev=0 if math.isnan(P_GFA_GT3_dev) else None
        P_GFA_GT4_dev = np.std(P_GFA_GT4_vec);# P_GFA_GT4_dev=0 if math.isnan(P_GFA_GT4_dev) else None
        P_GFC_GT1_dev = np.std(P_GFC_GT1_vec);# P_GFC_GT1_dev=0 if math.isnan(P_GFC_GT1_dev) else None   
        P_GFC_GT2_dev = np.std(P_GFC_GT2_vec);# P_GFC_GT2_dev=0 if math.isnan(P_GFC_GT2_dev) else None 
        P_GFC_GT3_dev = np.std(P_GFC_GT3_vec);# P_GFC_GT3_dev=0 if math.isnan(P_GFC_GT3_dev) else None         
        
        
        P_imbalance = P_GFA_GT1+P_GFA_GT2+P_GFA_GT3+P_GFA_GT4+P_GFC_GT1+P_GFC_GT2+P_GFC_GT3+P_WT-(P_dem_GFA+P_dem_GFB+P_dem_GFC+P_ELH_GFA+P_ELH_GFB+P_ELH_GFC+P_GFA_to_ELZ+P_loss_GFA_GFB_transmission+P_loss_GFA_GFC_transmission)
        
        
        cost_total = cost_NG + cost_NG_tax + cost_NOx_tax + cost_MNT_GT_total
        
        penalty_total = penalty_H2 + penalty_P_imbalance
        

        cost_NG_vec.append(cost_NG)
        cost_NG_tax_vec.append(cost_NG_tax)
        cost_NOx_tax_vec.append(cost_NOx_tax)
        cost_MNT_GT_total_vec.append(cost_MNT_GT_total)
        cost_total_vec.append(cost_total)
        penalty_H2_vec.append(penalty_H2)
        penalty_P_imbalance_vec.append(penalty_P_imbalance)
        penalty_total_vec.append(penalty_total)
        
        P_imbalance_GFA_vec.append(P_imbalance_GFA)
        P_imbalance_GFB_vec.append(P_imbalance_GFB)
        
        P_imbalance_GFC_vec.append(P_imbalance_GFC)
        P_GFA_GT1_vec.append(P_GFA_GT1)
        P_GFA_GT2_vec.append(P_GFA_GT2)
        P_GFA_GT3_vec.append(P_GFA_GT3)
        P_GFA_GT4_vec.append(P_GFA_GT4)
        P_GFC_GT1_vec.append(P_GFC_GT1)
        P_GFC_GT2_vec.append(P_GFC_GT2)
        P_GFC_GT3_vec.append(P_GFC_GT3) 
        
        P_GFA_to_GFB_vec.append(P_GFA_to_GFB)
        P_GFA_to_GFC_vec.append(P_GFA_to_GFC)
        P_GFB_from_GFA_vec.append(P_GFB_from_GFA)
        P_GFC_from_GFA_vec.append(P_GFC_from_GFA)
        P_GFA_from_GFC_vec.append(P_GFA_from_GFC)
        
        P_ELH_GFA_vec.append(P_ELH_GFA)
        P_ELH_GFB_vec.append(P_ELH_GFB)
        P_ELH_GFC_vec.append(P_ELH_GFC)        
        
        FR_GFA_GT1_vec.append(FR_GFA_GT1)
        FR_GFA_GT2_vec.append(FR_GFA_GT2)
        FR_GFA_GT3_vec.append(FR_GFA_GT3)
        FR_GFA_GT4_vec.append(FR_GFA_GT4)
        FR_GFC_GT1_vec.append(FR_GFC_GT1)
        FR_GFC_GT2_vec.append(FR_GFC_GT2)
        FR_GFC_GT3_vec.append(FR_GFC_GT3)         
        
        P_GFA_to_ELZ_vec.append(P_GFA_to_ELZ)

        
        H2_production_vec.append(H2_production) 
        H2_consumption_vec.append(H2_consumption)         
        
        m_NG_GFA_GT1_vec.append(m_f_NG_GFA_GT1)                              
        m_H2_GFA_GT1_vec.append(m_f_H2_GFA_GT1)                               
        m_NG_GFA_GT2_vec.append(m_f_NG_GFA_GT2)                                 
        m_H2_GFA_GT2_vec.append(m_f_H2_GFA_GT2)   
        m_NG_GFA_GT3_vec.append(m_f_NG_GFA_GT3)   
        m_H2_GFA_GT3_vec.append(m_f_H2_GFA_GT3)    
        m_NG_GFA_GT4_vec.append(m_f_NG_GFA_GT4)    
        m_H2_GFA_GT4_vec.append(m_f_H2_GFA_GT4)    
        m_NG_GFC_GT1_vec.append(m_f_NG_GFC_GT1)    
        m_H2_GFC_GT1_vec.append(m_f_H2_GFC_GT1)    
        m_NG_GFC_GT2_vec.append(m_f_NG_GFC_GT2)    
        m_H2_GFC_GT2_vec.append(m_f_H2_GFC_GT2)   
        m_NG_GFC_GT3_vec.append(m_f_NG_GFC_GT3)   
        m_H2_GFC_GT3_vec.append(m_f_H2_GFC_GT3) 
        
        eff_GFA_GT1_vec.append(eff_GFA_GT1)                              
        eff_GFA_GT2_vec.append(eff_GFA_GT2)                                 
        eff_GFA_GT3_vec.append(eff_GFA_GT3)   
        eff_GFA_GT4_vec.append(eff_GFA_GT4)    
        eff_GFC_GT1_vec.append(eff_GFC_GT1)    
        eff_GFC_GT2_vec.append(eff_GFC_GT2)    
        eff_GFC_GT3_vec.append(eff_GFC_GT3)     
        
        P_GFA_GT1_dev_vec.append(P_GFA_GT1_dev)
        P_GFA_GT2_dev_vec.append(P_GFA_GT2_dev)
        P_GFA_GT3_dev_vec.append(P_GFA_GT3_dev)
        P_GFA_GT4_dev_vec.append(P_GFA_GT4_dev) 
        P_GFC_GT1_dev_vec.append(P_GFC_GT1_dev)
        P_GFC_GT2_dev_vec.append(P_GFC_GT2_dev)
        P_GFC_GT3_dev_vec.append(P_GFC_GT3_dev)        
        P_imbalance_vec.append(P_imbalance)
        
        
    df_MG_round = pd.DataFrame({'P_GFA_GT1 [MW]':P_GFA_GT1_vec,
                            'P_GFA_GT2 [MW]':P_GFA_GT2_vec,
                            'P_GFA_GT3 [MW]':P_GFA_GT3_vec,
                            'P_GFA_GT4 [MW]':P_GFA_GT4_vec,
                            'P_GFC_GT1 [MW]':P_GFC_GT1_vec,
                            'P_GFC_GT2 [MW]':P_GFC_GT2_vec,
                            'P_GFC_GT3 [MW]':P_GFC_GT3_vec,                                
                            'FR_GFA_GT1 [-]':FR_GFA_GT1_vec,
                            'FR_GFA_GT2 [-]':FR_GFA_GT2_vec,
                            'FR_GFA_GT3 [-]':FR_GFA_GT3_vec,
                            'FR_GFA_GT4 [-]':FR_GFA_GT4_vec,
                            'FR_GFC_GT1 [-]':FR_GFC_GT1_vec,
                            'FR_GFC_GT2 [-]':FR_GFC_GT2_vec,
                            'FR_GFC_GT3 [-]':FR_GFC_GT3_vec,
                                
                            'm_NG_GFA_GT1 [kg/s]':m_NG_GFA_GT1_vec,                                
                            'm_H2_GFA_GT1 [kg/s]':m_H2_GFA_GT1_vec,                                
                            'm_NG_GFA_GT2 [kg/s]':m_NG_GFA_GT2_vec,                                
                            'm_H2_GFA_GT2 [kg/s]':m_H2_GFA_GT2_vec,  
                            'm_NG_GFA_GT3 [kg/s]':m_NG_GFA_GT3_vec,  
                            'm_H2_GFA_GT3 [kg/s]':m_H2_GFA_GT3_vec,  
                            'm_NG_GFA_GT4 [kg/s]':m_NG_GFA_GT4_vec,  
                            'm_H2_GFA_GT4 [kg/s]':m_H2_GFA_GT4_vec,  
                            'm_NG_GFC_GT1 [kg/s]':m_NG_GFC_GT1_vec,  
                            'm_H2_GFC_GT1 [kg/s]':m_H2_GFC_GT1_vec,  
                            'm_NG_GFC_GT2 [kg/s]':m_NG_GFC_GT2_vec,  
                            'm_H2_GFC_GT2 [kg/s]':m_H2_GFC_GT2_vec, 
                            'm_NG_GFC_GT3 [kg/s]':m_NG_GFC_GT3_vec,  
                            'm_H2_GFC_GT3 [kg/s]':m_H2_GFC_GT3_vec, 
                                
                            'eff_GFA_GT1 [-]':eff_GFA_GT1_vec, 
                            'eff_GFA_GT2 [-]':eff_GFA_GT2_vec, 
                            'eff_GFA_GT3 [-]':eff_GFA_GT3_vec, 
                            'eff_GFA_GT4 [-]':eff_GFA_GT4_vec, 
                            'eff_GFC_GT1 [-]':eff_GFC_GT1_vec, 
                            'eff_GFC_GT2 [-]':eff_GFC_GT2_vec, 
                            'eff_GFC_GT3 [-]':eff_GFC_GT3_vec,                                 
                                
                                
                            'P_imbalance_GFA [MW]':P_imbalance_GFA_vec,  
                            'P_imbalance_GFB [MW]':P_imbalance_GFB_vec,  
                            'P_imbalance_GFC [MW]':P_imbalance_GFC_vec, 

                            'P_GFA_to_GFB [MW]':P_GFA_to_GFB_vec, 
                            'P_GFB_from_GFA [MW]':P_GFB_from_GFA_vec, 
                            'P_GFA_to_GFC [MW]':P_GFA_to_GFC_vec, 
                            'P_GFA_from_GFC [MW]':P_GFA_from_GFC_vec, 
                            'P_GFC_from_GFA [MW]':P_GFC_from_GFA_vec,
                            'P_ELH_GFA [MW]':P_ELH_GFA_vec, 
                            'P_ELH_GFB [MW]':P_ELH_GFB_vec, 
                            'P_ELH_GFC [MW]':P_ELH_GFC_vec, 
                            'P_GFA_to_ELZ [MW]':P_GFA_to_ELZ_vec,
                                
                            'cost_NG [EUR]':cost_NG_vec,  
                            'cost_NG_tax [EUR]':cost_NG_tax_vec,
                            'cost_NOx_tax [EUR]':cost_NOx_tax_vec,
                            'cost_MNT_GT_total [EUR]':cost_MNT_GT_total_vec,  
                            'cost_total [EUR]':cost_total_vec,  
                            'penalty_H2 [EUR]':penalty_H2_vec,  
                            'penalty_P_imbalance [EUR]':penalty_P_imbalance_vec,  
                            'penalty_total [EUR]':penalty_total_vec,
                            'H2_production [kg/s]':H2_production_vec, 
                            'H2_consumption [kg/s]':H2_consumption_vec, 
                            'H2_tank_aval [kg/s]':H2_available_vec,  
                            'H2_tank_var [kg/s]':H2_variation_vec,
                            'P_GFA_GT1_dev [-]':P_GFA_GT1_dev_vec,
                            'P_GFA_GT2_dev [-]':P_GFA_GT2_dev_vec,
                            'P_GFA_GT3_dev [-]':P_GFA_GT3_dev_vec,
                            'P_GFA_GT4_dev [-]':P_GFA_GT4_dev_vec,                                
                            'P_GFC_GT1_dev [-]':P_GFC_GT1_dev_vec,
                            'P_GFC_GT2_dev [-]':P_GFC_GT2_dev_vec,
                            'P_GFC_GT3_dev [-]':P_GFC_GT3_dev_vec, 
                            'P_imbalance [MW]' : P_imbalance_vec,
                                
                            })

    df_MG_round = pd.concat([reserve_df, df_MG_round], axis=1)
        
    return df_MG_round, np.array(cost_total_vec).sum()/len(df_complete), np.array(penalty_total_vec).sum()/len(df_complete)



# In[ ]:


# New version with optimizer defining the connections and platform powers are optimized by a table-based function

def MG_run_evaluation(df_complete, x, parameter_definition, H2_tank_initial, x_band_statements, buy=True, sell=True):
    
    
    df_complete = df_complete.reset_index(drop=True)
    reserve_df = df_complete[['T_amb [degC]','P_dem_GFA [MW]','Q_dem_GFA [MW]','P_dem_GFB [MW]','Q_dem_GFB [MW]','P_dem_GFC [MW]','Q_dem_GFC [MW]','P_prod_WT [MW]']]
    
    # the NG price changes daily so it could be evaluated outside of the row loop
    
    Pr_NG = df_complete['NG_Price [EUR/MJ]'].iloc[0] #EUR/MJ
    Pr_NG_kg = Pr_NG*LHV_NG # EUR/kg
    reserve_df['NG_Price [EUR/kg]'] = Pr_NG_kg*np.ones(len(df_complete))    
    H2_available_vec = np.array([H2_tank_initial])
    H2_variation_vec = np.array([])
    
    delta_t = 60 * 60
    
    
    exec(parameter_definition)
    excess_power=[]
    for parameter_band_def in x_band_statements:
        exec(parameter_band_def)  
    
    # provide empty vectors
    for item in param_list:
        exp = item + '= set_zero_list("'+ item + '")'
        exec(exp,locals(),globals())
        

    for row in range(len(df_complete)):

        
# readings from the table
        T_amb = df_complete['T_amb [degC]'].iloc[row]
        P_dem_GFA = df_complete['P_dem_GFA [MW]'].iloc[row] #MW
        Q_dem_GFA = df_complete['Q_dem_GFA [MW]'].iloc[row] #MW
        P_dem_GFB = df_complete['P_dem_GFB [MW]'].iloc[row] #MW
        Q_dem_GFB = df_complete['Q_dem_GFB [MW]'].iloc[row] #MW        
        P_dem_GFC = df_complete['P_dem_GFC [MW]'].iloc[row] #MW
        Q_dem_GFC = df_complete['Q_dem_GFC [MW]'].iloc[row] #MW   
        P_WT = df_complete['P_prod_WT [MW]'].iloc[row] #MW
        
# evaluating the optimizing parameters
        if 'P_GFA_to_GFC_' in parameter_definition:
            min_P_GFA_to_GFC = eval('b_P_GFA_to_GFC_' + str(row) + '[0]')
            max_P_GFA_to_GFC = eval('b_P_GFA_to_GFC_' + str(row) + '[1]')
            P_GFA_to_GFC = eval('span_data_to_actual_data(P_GFA_to_GFC_' + str(row) + ', b_P_GFA_to_GFC_' + str(row) +')' )
        else:
            P_GFA_to_GFC = eval('b_P_GFA_to_GFC_' + str(row) + '[0]') # if the value is not set in X, then take the min value of the bound

        if 'P_GFA_to_ELZ_' in parameter_definition:
            min_P_GFA_to_ELZ = eval('b_P_GFA_to_ELZ_' + str(row) + '[0]')
            max_P_GFA_to_ELZ = eval('b_P_GFA_to_ELZ_' + str(row) + '[1]')
            P_GFA_to_ELZ = eval('span_data_to_actual_data(P_GFA_to_ELZ_' + str(row) + ', b_P_GFA_to_ELZ_' + str(row) +')' )
        else:
            P_GFA_to_ELZ_ = eval('b_P_GFA_to_ELZ_' + str(row) + '[0]') # if the value is not set in X, then take the min value of the bound

        if 'FR_GFA_GT1_' in parameter_definition:
            min_FR_GFA_GT1 = eval('b_FR_GFA_GT1_' + str(row) + '[0]')
            max_FR_GFA_GT1 = eval('b_FR_GFA_GT1_' + str(row) + '[1]')
            FR_GFA_GT1 = eval('span_data_to_actual_data(FR_GFA_GT1_' + str(row) + ', b_FR_GFA_GT1_' + str(row) +')' )
        else:
            FR_GFA_GT1 = eval('b_FR_GFA_GT1_' + str(row) + '[0]') # if the value is not set in X, then take the min value of the bound
                        
        FR_GFA_GT2 = 1; FR_GFA_GT3 = 1; FR_GFA_GT4 = 1  
        FR_GFC_GT1=1;FR_GFC_GT2=1;FR_GFC_GT3=1
        
# Writting energy balances:
# Heat balance for GFB:
        Q_ELH_GFB = Q_dem_GFB
        P_ELH_GFB = Q_ELH_GFB/electrical_heater_eff
# Power balance for GFB:
        P_GFA_to_GFB = (P_dem_GFB + P_ELH_GFB)/transfer_eff_P_GFA_to_GFB
        P_GFB_from_GFA = P_GFA_to_GFB * transfer_eff_P_GFA_to_GFB
        if P_GFA_to_GFB > max_P_GFA_to_GFB:
            P_GFA_to_GFB = max_P_GFA_to_GFB
            print('Warning! the required power in GFB is not satidfied!')
        P_imbalance_GFB = 0
        P_loss_GFA_GFB_transmission = P_GFA_to_GFB*(1-transfer_eff_P_GFA_to_GFB)
        
        
        
# Heat balance for GFC:
        if P_GFA_to_GFC>=0: # the direction is from A to C
            P_GFC_from_GFA = P_GFA_to_GFC * transfer_eff_P_GFA_to_GFC
            P_GFA_from_GFC = 0
            P_dem_GFC_net = P_dem_GFC - P_GFC_from_GFA
            P_loss_GFA_GFC_transmission = P_GFA_to_GFC*(1-transfer_eff_P_GFA_to_GFC)
        else: # the direction is from C to A
            P_GFA_from_GFC = abs(P_GFA_to_GFC)
            P_GFC_from_GFA = 0
            P_dem_GFC_net = P_dem_GFC + abs(P_GFA_to_GFC)/transfer_eff_P_GFA_to_GFC
            P_loss_GFA_GFC_transmission = abs(P_GFA_to_GFC/transfer_eff_P_GFA_to_GFC - P_GFA_to_GFC)
        impossibility_cost_GFC, optimum_GFC = GFC_operation_Opt(T_amb,P_dem_GFC_net,Q_dem_GFC,FR_GFC_GT1,FR_GFC_GT2,FR_GFC_GT3,Pr_NG_kg,delta_t)
        P_GFC_GT1,P_GFC_GT2,P_GFC_GT3,P_GFC_GTs_total,P_ELH_GFC,        Q_max_GFC_GT1,Q_max_GFC_GT2,Q_max_GFC_GT3,Q_max_GFC_GTs_total,        fuel_input_GFC_GT1,fuel_input_GFC_GT2,fuel_input_GFC_GT3,        fuel_input_NG_GFC_GT1,fuel_input_H2_GFC_GT1,        fuel_input_NG_GFC_GT2,fuel_input_H2_GFC_GT2,        fuel_input_NG_GFC_GT3,fuel_input_H2_GFC_GT3,        m_f_NG_GFC_GT1,m_f_NG_GFC_GT2,m_f_NG_GFC_GT3,        m_f_H2_GFC_GT1,m_f_H2_GFC_GT2,m_f_H2_GFC_GT3,        m_f_NG_total_GFC,m_f_H2_total_GFC,        cost_NG_GFC,cost_NG_tax_GFC,cost_NOx_tax_GFC,cost_MNT_GT_total_GFC,cost_total_GFC = optimum_GFC
        P_imbalance_GFC = impossibility_cost_GFC
        P_imbalance_GFC = (P_GFC_GT1+P_GFC_GT2+P_GFC_GT3)-(P_dem_GFC_net+P_ELH_GFC)
        
# Heat balance for GFA:
        P_dem_GFA_net = P_dem_GFA + P_GFA_to_GFB + P_GFA_to_GFC + P_GFA_to_ELZ+                        -(abs(P_WT))
        impossibility_cost_GFA, optimum_GFA = GFA_operation_Opt(T_amb,P_dem_GFA_net,Q_dem_GFA,FR_GFA_GT1,FR_GFA_GT2,FR_GFA_GT3,FR_GFA_GT4,H2_available_vec[row],Pr_NG_kg,delta_t)
        P_GFA_GT1,P_GFA_GT2,P_GFA_GT3,P_GFA_GT4,P_GFA_GTs_total,P_ELH_GFA,        Q_max_GFA_GT1,Q_max_GFA_GT2,Q_max_GFA_GT3,Q_max_GFA_GT4,Q_max_GFA_GTs_total,        fuel_input_GFA_GT1,fuel_input_GFA_GT2,fuel_input_GFA_GT3,fuel_input_GFA_GT4,        fuel_input_NG_GFA_GT1,fuel_input_H2_GFA_GT1,        fuel_input_NG_GFA_GT2,fuel_input_H2_GFA_GT2,        fuel_input_NG_GFA_GT3,fuel_input_H2_GFA_GT3,        fuel_input_NG_GFA_GT4,fuel_input_H2_GFA_GT4,        m_f_NG_GFA_GT1,m_f_NG_GFA_GT2,m_f_NG_GFA_GT3,m_f_NG_GFA_GT4,        m_f_H2_GFA_GT1,m_f_H2_GFA_GT2,m_f_H2_GFA_GT3,m_f_H2_GFA_GT4,        m_f_NG_total_GFA,m_f_H2_total_GFA,        cost_NG_GFA,cost_NG_tax_GFA,cost_NOx_tax_GFA,cost_MNT_GT_total_GFA,cost_total_GFA = optimum_GFA
        P_imbalance_GFA = impossibility_cost_GFA        
        
        
        P_imbalance_GFA = (P_GFA_GT1+P_GFA_GT2+P_GFA_GT3+P_GFA_GT4+P_WT)-(P_dem_GFA+P_ELH_GFA+P_GFA_to_GFB+P_GFA_to_ELZ+P_GFA_to_GFC)
        
        
        eff_GFA_GT1 = P_GFA_GT1/fuel_input_GFA_GT1;
        eff_GFA_GT2 = P_GFA_GT2/fuel_input_GFA_GT2;
        eff_GFA_GT3 = P_GFA_GT3/fuel_input_GFA_GT3;
        eff_GFA_GT4 = P_GFA_GT4/fuel_input_GFA_GT4;
        eff_GFC_GT1 = P_GFC_GT1/fuel_input_GFC_GT1;
        eff_GFC_GT2 = P_GFC_GT2/fuel_input_GFC_GT2;
        eff_GFC_GT3 = P_GFC_GT3/fuel_input_GFC_GT3;        
        

# Calculation of all the power provided to the electrolyzer
        P_ELZ = P_GFA_to_ELZ
#         H2_produced = electrolyzer_efficiency * P_ELZ/LHV_H2
        H2_produced = electrolyzer_prod(P_ELZ)
        if H2_produced < 0:
            H2_produced = 0        
        H2_production = H2_produced
# Cost calculation:
        cost_MNT_GT_total = cost_MNT_GT_total_GFA + cost_MNT_GT_total_GFC
        m_f_NG_total = m_f_NG_total_GFA + m_f_NG_total_GFC
        cost_NG = cost_NG_GFA + cost_NG_GFC
        cost_NG_tax = cost_NG_tax_GFA + cost_NG_tax_GFC
        cost_NOx_tax = cost_NOx_tax_GFA + cost_NOx_tax_GFC
        m_f_H2_total = m_f_H2_total_GFA + m_f_H2_total_GFC
        H2_consumption = m_f_H2_total
        H2_variation_vec = np.append(H2_variation_vec,H2_produced-m_f_H2_total)
        if row <len(df_complete)-1:
            H2_available_vec = np.append(H2_available_vec,H2_available_vec[0] + np.array(H2_variation_vec).sum())
        
        
        if H2_available_vec[row]-m_f_H2_total< 0:
            penalty_H2 = expense_H2_imbalance * abs(H2_available_vec[row]-m_f_H2_total)
        else: 
            penalty_H2 = 0
        
        penalty_P_imbalance = impossibility_cost_GFA + impossibility_cost_GFC
        
        P_GFA_GT1_dev = np.std(P_GFA_GT1_vec);# P_GFA_GT1_dev=0 if math.isnan(P_GFA_GT1_dev) else None
        P_GFA_GT2_dev = np.std(P_GFA_GT2_vec);# P_GFA_GT2_dev=0 if math.isnan(P_GFA_GT2_dev) else None
        P_GFA_GT3_dev = np.std(P_GFA_GT3_vec);# P_GFA_GT3_dev=0 if math.isnan(P_GFA_GT3_dev) else None
        P_GFA_GT4_dev = np.std(P_GFA_GT4_vec);# P_GFA_GT4_dev=0 if math.isnan(P_GFA_GT4_dev) else None
        P_GFC_GT1_dev = np.std(P_GFC_GT1_vec);# P_GFC_GT1_dev=0 if math.isnan(P_GFC_GT1_dev) else None   
        P_GFC_GT2_dev = np.std(P_GFC_GT2_vec);# P_GFC_GT2_dev=0 if math.isnan(P_GFC_GT2_dev) else None 
        P_GFC_GT3_dev = np.std(P_GFC_GT3_vec);# P_GFC_GT3_dev=0 if math.isnan(P_GFC_GT3_dev) else None         
        
        
        P_imbalance = P_GFA_GT1+P_GFA_GT2+P_GFA_GT3+P_GFA_GT4+P_GFC_GT1+P_GFC_GT2+P_GFC_GT3+P_WT-(P_dem_GFA+P_dem_GFB+P_dem_GFC+P_ELH_GFA+P_ELH_GFB+P_ELH_GFC+P_GFA_to_ELZ+P_loss_GFA_GFB_transmission+P_loss_GFA_GFC_transmission)
        
        cost_total = cost_NG + cost_NG_tax + cost_NOx_tax + cost_MNT_GT_total
        
        penalty_total = penalty_H2 + penalty_P_imbalance
        

        cost_NG_vec.append(cost_NG)
        cost_NG_tax_vec.append(cost_NG_tax)
        cost_NOx_tax_vec.append(cost_NOx_tax)
        cost_MNT_GT_total_vec.append(cost_MNT_GT_total)
        cost_total_vec.append(cost_total)
        penalty_H2_vec.append(penalty_H2)
        penalty_P_imbalance_vec.append(penalty_P_imbalance)
        penalty_total_vec.append(penalty_total)
        
        P_imbalance_GFA_vec.append(P_imbalance_GFA)
        P_imbalance_GFB_vec.append(P_imbalance_GFB)
        
        P_imbalance_GFC_vec.append(P_imbalance_GFC)
        P_GFA_GT1_vec.append(P_GFA_GT1)
        P_GFA_GT2_vec.append(P_GFA_GT2)
        P_GFA_GT3_vec.append(P_GFA_GT3)
        P_GFA_GT4_vec.append(P_GFA_GT4)
        P_GFC_GT1_vec.append(P_GFC_GT1)
        P_GFC_GT2_vec.append(P_GFC_GT2)
        P_GFC_GT3_vec.append(P_GFC_GT3) 
        
        P_GFA_to_GFB_vec.append(P_GFA_to_GFB)
        P_GFA_to_GFC_vec.append(P_GFA_to_GFC)
        P_GFB_from_GFA_vec.append(P_GFB_from_GFA)
        P_GFC_from_GFA_vec.append(P_GFC_from_GFA)
        P_GFA_from_GFC_vec.append(P_GFA_from_GFC)
        
        P_ELH_GFA_vec.append(P_ELH_GFA)
        P_ELH_GFB_vec.append(P_ELH_GFB)
        P_ELH_GFC_vec.append(P_ELH_GFC)
        
        
        FR_GFA_GT1_vec.append(FR_GFA_GT1)
        FR_GFA_GT2_vec.append(FR_GFA_GT2)
        FR_GFA_GT3_vec.append(FR_GFA_GT3)
        FR_GFA_GT4_vec.append(FR_GFA_GT4)
        FR_GFC_GT1_vec.append(FR_GFC_GT1)
        FR_GFC_GT2_vec.append(FR_GFC_GT2)
        FR_GFC_GT3_vec.append(FR_GFC_GT3)         
        
        P_GFA_to_ELZ_vec.append(P_GFA_to_ELZ)
        H2_production_vec.append(H2_production) 
        H2_consumption_vec.append(H2_consumption)         
        
        m_NG_GFA_GT1_vec.append(m_f_NG_GFA_GT1)                              
        m_H2_GFA_GT1_vec.append(m_f_H2_GFA_GT1)                               
        m_NG_GFA_GT2_vec.append(m_f_NG_GFA_GT2)                                 
        m_H2_GFA_GT2_vec.append(m_f_H2_GFA_GT2)   
        m_NG_GFA_GT3_vec.append(m_f_NG_GFA_GT3)   
        m_H2_GFA_GT3_vec.append(m_f_H2_GFA_GT3)    
        m_NG_GFA_GT4_vec.append(m_f_NG_GFA_GT4)    
        m_H2_GFA_GT4_vec.append(m_f_H2_GFA_GT4)    
        m_NG_GFC_GT1_vec.append(m_f_NG_GFC_GT1)    
        m_H2_GFC_GT1_vec.append(m_f_H2_GFC_GT1)    
        m_NG_GFC_GT2_vec.append(m_f_NG_GFC_GT2)    
        m_H2_GFC_GT2_vec.append(m_f_H2_GFC_GT2)   
        m_NG_GFC_GT3_vec.append(m_f_NG_GFC_GT3)   
        m_H2_GFC_GT3_vec.append(m_f_H2_GFC_GT3) 
        
        eff_GFA_GT1_vec.append(eff_GFA_GT1)                              
        eff_GFA_GT2_vec.append(eff_GFA_GT2)                                 
        eff_GFA_GT3_vec.append(eff_GFA_GT3)   
        eff_GFA_GT4_vec.append(eff_GFA_GT4)    
        eff_GFC_GT1_vec.append(eff_GFC_GT1)    
        eff_GFC_GT2_vec.append(eff_GFC_GT2)    
        eff_GFC_GT3_vec.append(eff_GFC_GT3)     
        
        P_GFA_GT1_dev_vec.append(P_GFA_GT1_dev)
        P_GFA_GT2_dev_vec.append(P_GFA_GT2_dev)
        P_GFA_GT3_dev_vec.append(P_GFA_GT3_dev)
        P_GFA_GT4_dev_vec.append(P_GFA_GT4_dev) 
        P_GFC_GT1_dev_vec.append(P_GFC_GT1_dev)
        P_GFC_GT2_dev_vec.append(P_GFC_GT2_dev)
        P_GFC_GT3_dev_vec.append(P_GFC_GT3_dev)        
        P_imbalance_vec.append(P_imbalance)
        
    df_MG_round = pd.DataFrame({'P_GFA_GT1 [MW]':P_GFA_GT1_vec,
                            'P_GFA_GT2 [MW]':P_GFA_GT2_vec,
                            'P_GFA_GT3 [MW]':P_GFA_GT3_vec,
                            'P_GFA_GT4 [MW]':P_GFA_GT4_vec,
                            'P_GFC_GT1 [MW]':P_GFC_GT1_vec,
                            'P_GFC_GT2 [MW]':P_GFC_GT2_vec,
                            'P_GFC_GT3 [MW]':P_GFC_GT3_vec,                                
                            'FR_GFA_GT1 [-]':FR_GFA_GT1_vec,
                            'FR_GFA_GT2 [-]':FR_GFA_GT2_vec,
                            'FR_GFA_GT3 [-]':FR_GFA_GT3_vec,
                            'FR_GFA_GT4 [-]':FR_GFA_GT4_vec,
                            'FR_GFC_GT1 [-]':FR_GFC_GT1_vec,
                            'FR_GFC_GT2 [-]':FR_GFC_GT2_vec,
                            'FR_GFC_GT3 [-]':FR_GFC_GT3_vec,
                                
                            'm_NG_GFA_GT1 [kg/s]':m_NG_GFA_GT1_vec,                                
                            'm_H2_GFA_GT1 [kg/s]':m_H2_GFA_GT1_vec,                                
                            'm_NG_GFA_GT2 [kg/s]':m_NG_GFA_GT2_vec,                                
                            'm_H2_GFA_GT2 [kg/s]':m_H2_GFA_GT2_vec,  
                            'm_NG_GFA_GT3 [kg/s]':m_NG_GFA_GT3_vec,  
                            'm_H2_GFA_GT3 [kg/s]':m_H2_GFA_GT3_vec,  
                            'm_NG_GFA_GT4 [kg/s]':m_NG_GFA_GT4_vec,  
                            'm_H2_GFA_GT4 [kg/s]':m_H2_GFA_GT4_vec,  
                            'm_NG_GFC_GT1 [kg/s]':m_NG_GFC_GT1_vec,  
                            'm_H2_GFC_GT1 [kg/s]':m_H2_GFC_GT1_vec,  
                            'm_NG_GFC_GT2 [kg/s]':m_NG_GFC_GT2_vec,  
                            'm_H2_GFC_GT2 [kg/s]':m_H2_GFC_GT2_vec, 
                            'm_NG_GFC_GT3 [kg/s]':m_NG_GFC_GT3_vec,  
                            'm_H2_GFC_GT3 [kg/s]':m_H2_GFC_GT3_vec, 
                                
                            'eff_GFA_GT1 [-]':eff_GFA_GT1_vec, 
                            'eff_GFA_GT2 [-]':eff_GFA_GT2_vec, 
                            'eff_GFA_GT3 [-]':eff_GFA_GT3_vec, 
                            'eff_GFA_GT4 [-]':eff_GFA_GT4_vec, 
                            'eff_GFC_GT1 [-]':eff_GFC_GT1_vec, 
                            'eff_GFC_GT2 [-]':eff_GFC_GT2_vec, 
                            'eff_GFC_GT3 [-]':eff_GFC_GT3_vec,                                 
                                
                                
                            'P_imbalance_GFA [MW]':P_imbalance_GFA_vec,  
                            'P_imbalance_GFB [MW]':P_imbalance_GFB_vec,  
                            'P_imbalance_GFC [MW]':P_imbalance_GFC_vec, 

                            'P_GFA_to_GFB [MW]':P_GFA_to_GFB_vec, 
                            'P_GFB_from_GFA [MW]':P_GFB_from_GFA_vec, 
                            'P_GFA_to_GFC [MW]':P_GFA_to_GFC_vec, 
                            'P_GFA_from_GFC [MW]':P_GFA_from_GFC_vec, 
                            'P_GFC_from_GFA [MW]':P_GFC_from_GFA_vec,
                            'P_ELH_GFA [MW]':P_ELH_GFA_vec, 
                            'P_ELH_GFB [MW]':P_ELH_GFB_vec, 
                            'P_ELH_GFC [MW]':P_ELH_GFC_vec, 
                            'P_GFA_to_ELZ [MW]':P_GFA_to_ELZ_vec,
                                
                            'cost_NG [EUR]':cost_NG_vec,  
                            'cost_NG_tax [EUR]':cost_NG_tax_vec,
                            'cost_NOx_tax [EUR]':cost_NOx_tax_vec,
                            'cost_MNT_GT_total [EUR]':cost_MNT_GT_total_vec,  
                            'cost_total [EUR]':cost_total_vec,  
                            'penalty_H2 [EUR]':penalty_H2_vec,  
                            'penalty_P_imbalance [EUR]':penalty_P_imbalance_vec,  
                            'penalty_total [EUR]':penalty_total_vec,
                            'H2_production [kg/s]':H2_production_vec, 
                            'H2_consumption [kg/s]':H2_consumption_vec, 
                            'H2_tank_aval [kg/s]':H2_available_vec,  
                            'H2_tank_var [kg/s]':H2_variation_vec,
                            'P_GFA_GT1_dev [-]':P_GFA_GT1_dev_vec,
                            'P_GFA_GT2_dev [-]':P_GFA_GT2_dev_vec,
                            'P_GFA_GT3_dev [-]':P_GFA_GT3_dev_vec,
                            'P_GFA_GT4_dev [-]':P_GFA_GT4_dev_vec,                                
                            'P_GFC_GT1_dev [-]':P_GFC_GT1_dev_vec,
                            'P_GFC_GT2_dev [-]':P_GFC_GT2_dev_vec,
                            'P_GFC_GT3_dev [-]':P_GFC_GT3_dev_vec, 
                            'P_imbalance [MW]' : P_imbalance_vec,
                                
                            })

    df_MG_round = pd.concat([reserve_df, df_MG_round], axis=1)
    
    return df_MG_round, np.array(cost_total_vec).sum()/len(df_complete), np.array(penalty_total_vec).sum()/len(df_complete)



# In[1]:


def MG_run_cb(df_complete, H2_tank_initial, x_band_statements, buy=True, sell=True):
    

    df_complete = df_complete.reset_index(drop=True)

#    P_GFA_to_ELZ = 0 #@
    
    reserve_df = df_complete[['T_amb [degC]','P_dem_GFA [MW]','Q_dem_GFA [MW]','P_dem_GFB [MW]','Q_dem_GFB [MW]','P_dem_GFC [MW]','Q_dem_GFC [MW]','P_prod_WT [MW]']]
    
    # the NG price changes daily so it could be evaluated outside of the row loop
    
    Pr_NG = df_complete['NG_Price [EUR/MJ]'].iloc[0] #EUR/MJ
    Pr_NG_kg = Pr_NG*LHV_NG # EUR/kg
    reserve_df['NG_Price [EUR/kg]'] = Pr_NG_kg*np.ones(len(df_complete))

    
    
    H2_available_vec = np.array([H2_tank_initial])
    H2_variation_vec = np.array([])
    
    delta_t = 60 * 60
    
    

    for parameter_band_def in x_band_statements:
        exec(parameter_band_def)  
    
    # provide empty vectors
    for item in param_list:
        exp = item + '= set_zero_list("'+ item + '")'
        exec(exp,locals(),globals())
        
    for row in range(len(df_complete)):
        P_imbalance_GFA = 0
        P_imbalance_GFB = 0
        P_imbalance_GFC = 0
        available_H2_current = H2_available_vec[row]
        
# readings from the table
        T_amb = df_complete['T_amb [degC]'].iloc[row]
        P_dem_GFA = df_complete['P_dem_GFA [MW]'].iloc[row] #MW
        Q_dem_GFA = df_complete['Q_dem_GFA [MW]'].iloc[row] #MW
        P_dem_GFB = df_complete['P_dem_GFB [MW]'].iloc[row] #MW
        Q_dem_GFB = df_complete['Q_dem_GFB [MW]'].iloc[row] #MW        
        P_dem_GFC = df_complete['P_dem_GFC [MW]'].iloc[row] #MW
        Q_dem_GFC = df_complete['Q_dem_GFC [MW]'].iloc[row] #MW   
        P_WT = df_complete['P_prod_WT [MW]'].iloc[row] #MW
    
# Writting energy balances:
# Heat and power balance for GFC:
        P_GFA_to_GFB, P_ELH_GFB = GFB_management(P_dem_GFB, Q_dem_GFB)
        P_GFB_from_GFA = P_GFA_to_GFB * transfer_eff_P_GFA_to_GFB
    
    
    
# Heat and power balance for GFC:
        P_GFC_GT1, P_GFC_GT2, P_GFC_GT3, P_GFA_to_GFC, P_ELH_GFC = GFC_management(T_amb, P_dem_GFC,Q_dem_GFC)
        
        if P_GFA_to_GFC > 0:
            P_GFC_from_GFA = P_GFA_to_GFC * transfer_eff_P_GFA_to_GFB
            P_GFA_from_GFC = 0
        else:
            P_GFA_from_GFC = -P_GFA_to_GFC
            P_GFC_from_GFA = 0


# Heat and power balance for GFA:
#         P_GFA_GT1, P_GFA_GT2, P_GFA_GT3,  P_GFA_GT4, Q_GFA_GT1, Q_GFA_GT2, Q_GFA_GT3,  Q_GFA_GT4, P_GFA_to_ELZ, P_ELH_GFA = GFA_management(T_amb, P_dem_GFA, Q_dem_GFA, P_GFA_to_GFB, P_GFA_to_GFC, P_WT)
        P_GFA_GT1, P_GFA_GT2, P_GFA_GT3,  P_GFA_GT4, P_GFA_to_ELZ, P_ELH_GFA = GFA_management(T_amb, P_dem_GFA, Q_dem_GFA, P_GFA_to_GFB, P_GFA_to_GFC, P_WT)

        m_f_GFA_GT1, fuel_input_GFA_GT1, eff_GFA_GT1, TOT_GFA_GT1 = LM25PE(model_MGT, P_GFA_GT1, T_amb, scaler=scaler_MGT)        
        m_f_GFA_GT2, fuel_input_GFA_GT2, eff_GFA_GT2, TOT_GFA_GT2 = LM25PE(model_MGT, P_GFA_GT2, T_amb, scaler=scaler_MGT)        
        m_f_GFA_GT3, fuel_input_GFA_GT3, eff_GFA_GT3, TOT_GFA_GT3 = LM25PE(model_MGT, P_GFA_GT3, T_amb, scaler=scaler_MGT)        
        m_f_GFA_GT4, fuel_input_GFA_GT4, eff_GFA_GT4, TOT_GFA_GT4 = LM25PE(model_MGT, P_GFA_GT4, T_amb, scaler=scaler_MGT)        
        m_f_GFC_GT1, fuel_input_GFC_GT1, eff_GFC_GT1, TOT_GFC_GT1 = LM25PE(model_MGT, P_GFC_GT1, T_amb, scaler=scaler_MGT)        
        m_f_GFC_GT2, fuel_input_GFC_GT2, eff_GFC_GT2, TOT_GFC_GT2 = LM25PE(model_MGT, P_GFC_GT2, T_amb, scaler=scaler_MGT)        
        m_f_GFC_GT3, fuel_input_GFC_GT3, eff_GFC_GT3, TOT_GFC_GT3 = LM25PE(model_MGT, P_GFC_GT3, T_amb, scaler=scaler_MGT)        
        


# Calculation of all the power provided to the electrolyzer
        P_WT_to_ELZ = 0
        P_ELZ = P_GFA_to_ELZ + P_WT_to_ELZ
        P_GFA_to_ELZ = P_ELZ
        H2_produced = electrolyzer_prod(P_ELZ)
        if H2_produced < 0:
            H2_produced = 0    
    
        H2_production = H2_produced
        
        
# evaluating the optimizing parameters
        available_H2_HV = available_H2_current * LHV_H2
        required_HV = fuel_input_GFA_GT1# only GFA GT1can run with H2
       
        FR_GFA_GT2 = 1
        FR_GFA_GT3 = 1
        FR_GFA_GT4 = 1
        FR_GFC_GT1 = 1
        FR_GFC_GT2 = 1
        FR_GFC_GT3 = 1
        
        if available_H2_HV < 0:
            available_H2_HV = 0
        
        if required_HV <= available_H2_HV:
            FR_GFA_GT1 = FR_min
        else:
            
            FR_GFA_GT1 = 1-(available_H2_HV/required_HV)
            
            if FR_GFA_GT1<FR_min:
                FR_GFA_GT1 = FR_min
                
        fuel_input_NG_GFA_GT1 = FR_GFA_GT1 * fuel_input_GFA_GT1; m_f_NG_GFA_GT1 = fuel_input_NG_GFA_GT1/LHV_NG
        fuel_input_H2_GFA_GT1 = (1-FR_GFA_GT1) * fuel_input_GFA_GT1; m_f_H2_GFA_GT1 = fuel_input_H2_GFA_GT1/LHV_H2 
        fuel_input_NG_GFA_GT2 = FR_GFA_GT2 * fuel_input_GFA_GT2; m_f_NG_GFA_GT2 = fuel_input_NG_GFA_GT2/LHV_NG
        fuel_input_H2_GFA_GT2 = (1-FR_GFA_GT2) * fuel_input_GFA_GT2; m_f_H2_GFA_GT2 = fuel_input_H2_GFA_GT2/LHV_H2 
        fuel_input_NG_GFA_GT3 = FR_GFA_GT3 * fuel_input_GFA_GT3; m_f_NG_GFA_GT3 = fuel_input_NG_GFA_GT3/LHV_NG
        fuel_input_H2_GFA_GT3 = (1-FR_GFA_GT3) * fuel_input_GFA_GT3; m_f_H2_GFA_GT3 = fuel_input_H2_GFA_GT3/LHV_H2 
        fuel_input_NG_GFA_GT4 = FR_GFA_GT4 * fuel_input_GFA_GT4; m_f_NG_GFA_GT4 = fuel_input_NG_GFA_GT4/LHV_NG
        fuel_input_H2_GFA_GT4 = (1-FR_GFA_GT4) * fuel_input_GFA_GT4; m_f_H2_GFA_GT4 = fuel_input_H2_GFA_GT4/LHV_H2         
        fuel_input_NG_GFC_GT1 = FR_GFC_GT1 * fuel_input_GFC_GT1; m_f_NG_GFC_GT1 = fuel_input_NG_GFC_GT1/LHV_NG
        fuel_input_H2_GFC_GT1 = (1-FR_GFC_GT1) * fuel_input_GFC_GT1; m_f_H2_GFC_GT1 = fuel_input_H2_GFC_GT1/LHV_H2 
        fuel_input_NG_GFC_GT2 = FR_GFC_GT2 * fuel_input_GFC_GT2; m_f_NG_GFC_GT2 = fuel_input_NG_GFC_GT2/LHV_NG
        fuel_input_H2_GFC_GT2 = (1-FR_GFC_GT2) * fuel_input_GFC_GT2; m_f_H2_GFC_GT2 = fuel_input_H2_GFC_GT2/LHV_H2 
        fuel_input_NG_GFC_GT3 = FR_GFC_GT3 * fuel_input_GFC_GT3; m_f_NG_GFC_GT3 = fuel_input_NG_GFC_GT3/LHV_NG
        fuel_input_H2_GFC_GT3 = (1-FR_GFC_GT3) * fuel_input_GFC_GT3; m_f_H2_GFC_GT3 = fuel_input_H2_GFC_GT3/LHV_H2 

        power_array  = np.array([P_GFA_GT1,P_GFA_GT2,P_GFA_GT3,P_GFA_GT4,P_GFC_GT1,P_GFC_GT2,P_GFC_GT3])
        NOx_produced_ = NOx_produced(power_array) 
        cost_NOx_tax = (NOx_produced_.sum())*NOx_tax/10 * delta_t # EUR, 10 is to change NOK to EUR
        
        eff_GFA_GT1 = P_GFA_GT1/fuel_input_GFA_GT1;
        eff_GFA_GT2 = P_GFA_GT2/fuel_input_GFA_GT2;
        eff_GFA_GT3 = P_GFA_GT3/fuel_input_GFA_GT3;
        eff_GFA_GT4 = P_GFA_GT4/fuel_input_GFA_GT4;
        
        eff_GFC_GT1 = P_GFC_GT1/fuel_input_GFC_GT1;
        eff_GFC_GT2 = P_GFC_GT2/fuel_input_GFC_GT2;
        eff_GFC_GT3 = P_GFC_GT3/fuel_input_GFC_GT3;        
        
# Cost calculation:
        cost_MNT_GFA_GT1 = LM25PE_MNT_cost(P_GFA_GT1)
        cost_MNT_GFA_GT2 = LM25PE_MNT_cost(P_GFA_GT2)
        cost_MNT_GFA_GT3 = LM25PE_MNT_cost(P_GFA_GT3)
        cost_MNT_GFA_GT4 = LM25PE_MNT_cost(P_GFA_GT4)
        cost_MNT_GFC_GT1 = LM25PE_MNT_cost(P_GFC_GT1)
        cost_MNT_GFC_GT2 = LM25PE_MNT_cost(P_GFC_GT2)
        cost_MNT_GFC_GT3 = LM25PE_MNT_cost(P_GFC_GT3)        
        
        cost_MNT_GT_total = cost_MNT_GFA_GT1 + cost_MNT_GFA_GT2 + cost_MNT_GFA_GT3 + cost_MNT_GFA_GT4 +        cost_MNT_GFC_GT1 + cost_MNT_GFC_GT2 + cost_MNT_GFC_GT3
        
         
        m_f_NG_total = m_f_NG_GFA_GT1 + m_f_NG_GFA_GT2 + m_f_NG_GFA_GT3 + m_f_NG_GFA_GT4 +        m_f_NG_GFC_GT1 + m_f_NG_GFC_GT2 + m_f_NG_GFC_GT3 
        
        cost_NG = m_f_NG_total * Pr_NG_kg * delta_t  # EUR
        
        cost_NG_tax = CO2_tax * m_f_NG_total * delta_t   # EUR



        
        m_f_H2_total = m_f_H2_GFA_GT1 + m_f_H2_GFA_GT2 + m_f_H2_GFA_GT3 + m_f_H2_GFA_GT4 +        m_f_H2_GFC_GT1 + m_f_H2_GFC_GT2 + m_f_H2_GFC_GT3 
        H2_consumption = m_f_H2_total
                
        
        H2_variation_vec = np.append(H2_variation_vec,H2_produced-H2_consumption)
        if row <len(df_complete)-1:
            H2_available_vec = np.append(H2_available_vec,H2_available_vec[0] + np.array(H2_variation_vec).sum())

        # more strict constraint, the available should be compared to the consumption
        if H2_available_vec[row]-m_f_H2_total< 0:
            penalty_H2 = expense_H2_imbalance * abs(H2_available_vec[row]-m_f_H2_total)
        else: 
            penalty_H2 = 0
        
             
        cost_P_imbalance_GFA = 0
        cost_P_imbalance_GFB = 0
        cost_P_imbalance_GFC = 0
    
        
        penalty_P_imbalance = cost_P_imbalance_GFB + cost_P_imbalance_GFC
               
        
        P_GFA_GT1_dev = np.std(P_GFA_GT1_vec);# P_GFA_GT1_dev=0 if math.isnan(P_GFA_GT1_dev) else None
        P_GFA_GT2_dev = np.std(P_GFA_GT2_vec);# P_GFA_GT2_dev=0 if math.isnan(P_GFA_GT2_dev) else None
        P_GFA_GT3_dev = np.std(P_GFA_GT3_vec);# P_GFA_GT3_dev=0 if math.isnan(P_GFA_GT3_dev) else None
        P_GFA_GT4_dev = np.std(P_GFA_GT4_vec);# P_GFA_GT4_dev=0 if math.isnan(P_GFA_GT4_dev) else None
        P_GFC_GT1_dev = np.std(P_GFC_GT1_vec);# P_GFC_GT1_dev=0 if math.isnan(P_GFC_GT1_dev) else None   
        P_GFC_GT2_dev = np.std(P_GFC_GT2_vec);# P_GFC_GT2_dev=0 if math.isnan(P_GFC_GT2_dev) else None 
        P_GFC_GT3_dev = np.std(P_GFC_GT3_vec);# P_GFC_GT3_dev=0 if math.isnan(P_GFC_GT3_dev) else None         
        
        
    
        P_imbalance = P_GFA_GT1+P_GFA_GT2+P_GFA_GT3+P_GFA_GT4+P_GFC_GT1+P_GFC_GT2+P_GFC_GT3+P_WT-(P_dem_GFA+P_dem_GFB+P_dem_GFC+P_ELH_GFA+P_ELH_GFB+P_ELH_GFC+P_GFA_to_ELZ)


        cost_total = cost_NG + cost_NG_tax + cost_MNT_GT_total + cost_NOx_tax
        penalty_total = penalty_H2 + penalty_P_imbalance
        

        cost_NG_vec.append(cost_NG)
        cost_NG_tax_vec.append(cost_NG_tax)
        cost_NOx_tax_vec.append(cost_NOx_tax)
        cost_MNT_GT_total_vec.append(cost_MNT_GT_total)
        cost_total_vec.append(cost_total)
        penalty_H2_vec.append(penalty_H2)
        penalty_P_imbalance_vec.append(penalty_P_imbalance)
        penalty_total_vec.append(penalty_total)
        
        P_GFA_GT1_vec.append(P_GFA_GT1)
        P_GFA_GT2_vec.append(P_GFA_GT2)
        P_GFA_GT3_vec.append(P_GFA_GT3)
        P_GFA_GT4_vec.append(P_GFA_GT4)
        P_GFC_GT1_vec.append(P_GFC_GT1)
        P_GFC_GT2_vec.append(P_GFC_GT2)
        P_GFC_GT3_vec.append(P_GFC_GT3) 
        
        P_GFA_to_GFB_vec.append(P_GFA_to_GFB)
        P_GFA_to_GFC_vec.append(P_GFA_to_GFC)
        P_GFB_from_GFA_vec.append(P_GFB_from_GFA)
        P_GFC_from_GFA_vec.append(P_GFC_from_GFA)
        P_GFA_from_GFC_vec.append(P_GFA_from_GFC)
        
        P_ELH_GFA_vec.append(P_ELH_GFA)
        P_ELH_GFB_vec.append(P_ELH_GFB)
        P_ELH_GFC_vec.append(P_ELH_GFC)
#         P_GFA_to_ELZ_vec.append(P_GFA_to_ELZ)
        
        
        FR_GFA_GT1_vec.append(FR_GFA_GT1)
        FR_GFA_GT2_vec.append(FR_GFA_GT2)
        FR_GFA_GT3_vec.append(FR_GFA_GT3)
        FR_GFA_GT4_vec.append(FR_GFA_GT4)
        FR_GFC_GT1_vec.append(FR_GFC_GT1)
        FR_GFC_GT2_vec.append(FR_GFC_GT2)
        FR_GFC_GT3_vec.append(FR_GFC_GT3)         
        P_GFA_to_ELZ_vec.append(P_GFA_to_ELZ)

        
        H2_production_vec.append(H2_production) 
        H2_consumption_vec.append(H2_consumption) 
        
        P_imbalance_GFA_vec.append(P_imbalance_GFA)
        P_imbalance_GFB_vec.append(P_imbalance_GFB)
        P_imbalance_GFC_vec.append(P_imbalance_GFC)
        
        
        m_NG_GFA_GT1_vec.append(m_f_NG_GFA_GT1)                              
        m_H2_GFA_GT1_vec.append(m_f_H2_GFA_GT1)                               
        m_NG_GFA_GT2_vec.append(m_f_NG_GFA_GT2)                                 
        m_H2_GFA_GT2_vec.append(m_f_H2_GFA_GT2)   
        m_NG_GFA_GT3_vec.append(m_f_NG_GFA_GT3)   
        m_H2_GFA_GT3_vec.append(m_f_H2_GFA_GT3)    
        m_NG_GFA_GT4_vec.append(m_f_NG_GFA_GT4)    
        m_H2_GFA_GT4_vec.append(m_f_H2_GFA_GT4)    
        m_NG_GFC_GT1_vec.append(m_f_NG_GFC_GT1)    
        m_H2_GFC_GT1_vec.append(m_f_H2_GFC_GT1)    
        m_NG_GFC_GT2_vec.append(m_f_NG_GFC_GT2)    
        m_H2_GFC_GT2_vec.append(m_f_H2_GFC_GT2)   
        m_NG_GFC_GT3_vec.append(m_f_NG_GFC_GT3)   
        m_H2_GFC_GT3_vec.append(m_f_H2_GFC_GT3)  
        
        eff_GFA_GT1_vec.append(eff_GFA_GT1)                              
        eff_GFA_GT2_vec.append(eff_GFA_GT2)                                 
        eff_GFA_GT3_vec.append(eff_GFA_GT3)   
        eff_GFA_GT4_vec.append(eff_GFA_GT4)    
        eff_GFC_GT1_vec.append(eff_GFC_GT1)    
        eff_GFC_GT2_vec.append(eff_GFC_GT2)    
        eff_GFC_GT3_vec.append(eff_GFC_GT3)   
        P_GFA_GT1_dev_vec.append(P_GFA_GT1_dev)
        P_GFA_GT2_dev_vec.append(P_GFA_GT2_dev)
        P_GFA_GT3_dev_vec.append(P_GFA_GT3_dev)
        P_GFA_GT4_dev_vec.append(P_GFA_GT4_dev) 
        P_GFC_GT1_dev_vec.append(P_GFC_GT1_dev)
        P_GFC_GT2_dev_vec.append(P_GFC_GT2_dev)
        P_GFC_GT3_dev_vec.append(P_GFC_GT3_dev)           
        
        P_imbalance_vec.append(P_imbalance)



    
    df_MG_round = pd.DataFrame({'P_GFA_GT1 [MW]':P_GFA_GT1_vec,
                            'P_GFA_GT2 [MW]':P_GFA_GT2_vec,
                            'P_GFA_GT3 [MW]':P_GFA_GT3_vec,
                            'P_GFA_GT4 [MW]':P_GFA_GT4_vec,
                            'P_GFC_GT1 [MW]':P_GFC_GT1_vec,
                            'P_GFC_GT2 [MW]':P_GFC_GT2_vec,
                            'P_GFC_GT3 [MW]':P_GFC_GT3_vec,                                
                            'FR_GFA_GT1 [-]':FR_GFA_GT1_vec,
                            'FR_GFA_GT2 [-]':FR_GFA_GT2_vec,
                            'FR_GFA_GT3 [-]':FR_GFA_GT3_vec,
                            'FR_GFA_GT4 [-]':FR_GFA_GT4_vec,
                            'FR_GFC_GT1 [-]':FR_GFC_GT1_vec,
                            'FR_GFC_GT2 [-]':FR_GFC_GT2_vec,
                            'FR_GFC_GT3 [-]':FR_GFC_GT3_vec,                                
                    
                            'm_NG_GFA_GT1 [kg/s]':m_NG_GFA_GT1_vec,                                
                            'm_H2_GFA_GT1 [kg/s]':m_H2_GFA_GT1_vec,                                
                            'm_NG_GFA_GT2 [kg/s]':m_NG_GFA_GT2_vec,                                
                            'm_H2_GFA_GT2 [kg/s]':m_H2_GFA_GT2_vec,  
                            'm_NG_GFA_GT3 [kg/s]':m_NG_GFA_GT3_vec,  
                            'm_H2_GFA_GT3 [kg/s]':m_H2_GFA_GT3_vec,  
                            'm_NG_GFA_GT4 [kg/s]':m_NG_GFA_GT4_vec,  
                            'm_H2_GFA_GT4 [kg/s]':m_H2_GFA_GT4_vec,  
                            'm_NG_GFC_GT1 [kg/s]':m_NG_GFC_GT1_vec,  
                            'm_H2_GFC_GT1 [kg/s]':m_H2_GFC_GT1_vec,  
                            'm_NG_GFC_GT2 [kg/s]':m_NG_GFC_GT2_vec,  
                            'm_H2_GFC_GT2 [kg/s]':m_H2_GFC_GT2_vec, 
                            'm_NG_GFC_GT3 [kg/s]':m_NG_GFC_GT3_vec,  
                            'm_H2_GFC_GT3 [kg/s]':m_H2_GFC_GT3_vec, 
                                
                                
                            'eff_GFA_GT1 [-]':eff_GFA_GT1_vec, 
                            'eff_GFA_GT2 [-]':eff_GFA_GT2_vec, 
                            'eff_GFA_GT3 [-]':eff_GFA_GT3_vec, 
                            'eff_GFA_GT4 [-]':eff_GFA_GT4_vec, 
                            'eff_GFC_GT1 [-]':eff_GFC_GT1_vec, 
                            'eff_GFC_GT2 [-]':eff_GFC_GT2_vec, 
                            'eff_GFC_GT3 [-]':eff_GFC_GT3_vec,                               
                                
                            'P_GFA_to_GFB [MW]':P_GFA_to_GFB_vec, 
                            'P_GFB_from_GFA [MW]':P_GFB_from_GFA_vec, 
                            'P_GFA_to_GFC [MW]':P_GFA_to_GFC_vec, 
                            'P_GFA_from_GFC [MW]':P_GFA_from_GFC_vec, 
                            'P_GFC_from_GFA [MW]':P_GFC_from_GFA_vec,
                            'P_ELH_GFA [MW]':P_ELH_GFA_vec, 
                            'P_ELH_GFB [MW]':P_ELH_GFB_vec, 
                            'P_ELH_GFC [MW]':P_ELH_GFC_vec, 
                            'P_GFA_to_ELZ [MW]':P_GFA_to_ELZ_vec,                                
                            'cost_NG [EUR]':cost_NG_vec,  
                            'cost_NG_tax [EUR]':cost_NG_tax_vec,  
                            'cost_NOx_tax [EUR]':cost_NOx_tax_vec,
                            'cost_MNT_GT_total [EUR]':cost_MNT_GT_total_vec,  
                            'cost_total [EUR]':cost_total_vec,  
                            'penalty_H2 [EUR]':penalty_H2_vec,  
                            'penalty_P_imbalance [EUR]':penalty_P_imbalance_vec,  
                            'penalty_total [EUR]':penalty_total_vec,
                            'H2_production [kg/s]':H2_production_vec, 
                            'H2_consumption [kg/s]':H2_consumption_vec, 
                            'H2_tank_aval [kg/s]':H2_available_vec,  
                            'H2_tank_var [kg/s]':H2_variation_vec,
                            'P_GFA_GT1_dev [-]':P_GFA_GT1_dev_vec,
                            'P_GFA_GT2_dev [-]':P_GFA_GT2_dev_vec,
                            'P_GFA_GT3_dev [-]':P_GFA_GT3_dev_vec,
                            'P_GFA_GT4_dev [-]':P_GFA_GT4_dev_vec,                                
                            'P_GFC_GT1_dev [-]':P_GFC_GT1_dev_vec,
                            'P_GFC_GT2_dev [-]':P_GFC_GT2_dev_vec,
                            'P_GFC_GT3_dev [-]':P_GFC_GT3_dev_vec,                                  
                            'P_imbalance [MW]' : P_imbalance_vec,
                                
                                
                                
                                
                            })
                                
                                
  

    
    
    df_MG_round = pd.concat([reserve_df, df_MG_round], axis=1)
    return df_MG_round, np.array(cost_total_vec).sum()/len(df_complete), np.array(penalty_total_vec).sum()/len(df_complete)
#     return df_MG_round, np.array(cost_total_vec).sum(), np.array(penalty_total_vec).sum()



# In[ ]:


def GFB_management(P_dem_GFB, Q_dem_GFB):

    Q_ELH_GFB = Q_dem_GFB
    P_ELH_GFB = Q_ELH_GFB/electrical_heater_eff
# Power balance for GFB:
    P_GFA_to_GFB = (P_dem_GFB + P_ELH_GFB)/transfer_eff_P_GFA_to_GFB
    P_GFB_from_GFA = P_GFA_to_GFB * transfer_eff_P_GFA_to_GFB
    if P_GFA_to_GFB > max_P_GFA_to_GFB:
        print('Warning! Demand on GFB is more than 20 MW')
        P_GFA_to_GFB = max_P_GFA_to_GFB
    return P_GFA_to_GFB, P_ELH_GFB


# In[ ]:



def GFC_management(T_amb, P_dem_GFC, Q_dem_GFC):
    sc = 'sc1'    
    
    P_GFC_GT1=0; P_GFC_GT2=0; P_GFC_GT3=0;
    Q_GFC_GT1=0; Q_GFC_GT2=0; Q_GFC_GT3=0;

    # First decide about the number of GTs to be on

    no_GT_GFC_Q_based = np.ceil(Q_dem_GFC/Q_max_acc_LM25PE)
    
    P_ELH_GFC = 0
    if no_GT_GFC_Q_based > 2:
        no_GT_GFC_Q_based = 2 # since there are only GT with Q production on GFC
        Q_ELH_GFC = (Q_dem_GFC - no_GT_GFC_Q_based*Q_max_acc_LM25PE)/electrical_heater_eff
    else:
        Q_ELH_GFC = 0

    P_ELH_GFC = Q_ELH_GFC


    no_GT_GFC_P_based = np.ceil((P_dem_GFC+P_ELH_GFC)/P_max_acc_LM25PE)
    if no_GT_GFC_P_based > 3:
        
        no_GT_GFC_P_based = 3

        P_GFC_GT1 = P_max_acc_LM25PE
        P_GFC_GT2 = P_max_acc_LM25PE
        P_GFC_GT3 = P_max_acc_LM25PE

        Q_max_GFC_GT1 = Q_max_acc_LM25PE
        Q_max_GFC_GT2 = Q_max_acc_LM25PE
        Q_max_GFC_GT3 = 0

        P_GFA_to_GFC = P_dem_GFC+P_ELH_GFC - 3 * P_max_acc_LM25PE

    else:
        
        P_GFA_to_GFC = 0
        no_GT_GFC = max(no_GT_GFC_P_based,no_GT_GFC_Q_based)



        if sc == 'sc1':
            P_GFC_GT1 = (P_dem_GFC+P_ELH_GFC)/no_GT_GFC
            
            if P_GFC_GT1<=P_min_acc_LM25PE:
                P_GFC_GT1 = P_min_acc_LM25PE
            if no_GT_GFC > 1:
                P_GFC_GT2 = P_GFC_GT1
                if no_GT_GFC > 2:
                    P_GFC_GT3 = P_GFC_GT2

            m_f_GFC_GT1, fuel_input_GFC_GT1, eff_GFC_GT1, TOT_GFC_GT1 =            LM25PE(model_MGT, P_GFC_GT1, T_amb, scaler=scaler_MGT)
            Q_max_GFC_GT1 = Q_max_LM25PE (P_GFC_GT1, TOT_GFC_GT1)     
            Q_max_GFC_GT2 = Q_max_GFC_GT1
            Q_max_GFC_GT3 = 0
            
    P_GFC_GTs = P_GFC_GT1+P_GFC_GT2+P_GFC_GT3
    Q_GFC_GTs = Q_GFC_GT1+Q_GFC_GT2+Q_GFC_GT3
    
    P_GFA_to_GFC = -(P_GFC_GTs - (P_dem_GFC+P_ELH_GFC))
    
    
    if P_GFA_to_GFC > 0: 
        P_GFA_to_GFC = -(P_GFC_GTs - (P_dem_GFC+P_ELH_GFC))/transfer_eff_P_GFA_to_GFC
    
    else:
        P_GFA_to_GFC = -(P_GFC_GTs - (P_dem_GFC+P_ELH_GFC))*transfer_eff_P_GFA_to_GFC
    
    
    if P_GFA_to_GFC < 0.1:
        P_GFA_to_GFC = 0
        
    P_GFC_GT1 = np.ceil(P_GFC_GT1); P_GFC_GT2 = np.ceil(P_GFC_GT2); P_GFC_GT3 = np.ceil(P_GFC_GT3)
    
    return P_GFC_GT1, P_GFC_GT2, P_GFC_GT3, P_GFA_to_GFC, P_ELH_GFC 
    


# In[ ]:




def GFA_management(T_amb, P_dem_GFA, Q_dem_GFA, P_GFA_to_GFB, P_GFA_to_GFC, P_WT):
    
    P_WT_to_GFA = P_WT # first assumption

    sc = 'sc1'    
    
    P_GFA_GT1=0; P_GFA_GT2=0; P_GFA_GT3=0; P_GFA_GT4=0;
    Q_GFC_GT1=0; Q_GFC_GT2=0; Q_GFC_GT3=0; Q_GFC_GT4=0;

    # First decide about the number of GTs to be on

    no_GT_GFA_Q_based = np.ceil(Q_dem_GFA/Q_max_acc_LM25PE)
    
    Q_ELH_GFA = 0
    if no_GT_GFA_Q_based > 3:
        no_GT_GFA_Q_based = 3 # since there are only 3 GT with Q production on GFC
        Q_ELH_GFC = (Q_dem_GFA - no_GT_GFA_Q_based*Q_max_acc_LM25PE)/electrical_heater_eff
    else:
        Q_ELH_GFA = 0

    P_ELH_GFA = Q_ELH_GFA


    no_GT_GFA_P_based = np.ceil((P_dem_GFA+P_ELH_GFA+P_GFA_to_GFB+P_GFA_to_GFC-P_WT_to_GFA)/P_max_acc_LM25PE)
    if no_GT_GFA_P_based < 0: # meaning that sum of P_WT and P_GFA_to_GFC (if coming from C to A) is so high that we don't need to run GTs
        
        
        no_GT_GFA_P_based = 0
        no_GT_GFA = max(no_GT_GFA_P_based,no_GT_GFA_Q_based)
    
    
    elif no_GT_GFA_P_based > 4:
#         print('type2')
        
        no_GT_GFA_P_based = 4

        P_GFA_GT1 = P_max_acc_LM25PE
        P_GFA_GT2 = P_max_acc_LM25PE
        P_GFA_GT3 = P_max_acc_LM25PE
        P_GFA_GT4 = P_max_acc_LM25PE
        

        Q_max_GFA_GT1 = Q_max_acc_LM25PE
        Q_max_GFA_GT2 = Q_max_acc_LM25PE
        Q_max_GFA_GT3 = Q_max_acc_LM25PE
        Q_max_GFA_GT4 =0
        
        P_GFA_imbalance = P_dem_GFA+P_ELH_GFA+P_GFA_to_GFB+P_GFA_to_GFC - 4 * P_max_acc_LM25PE
    else:

        
        P_GFA_to_ELZ = 0
        no_GT_GFA = max(no_GT_GFA_P_based,no_GT_GFA_Q_based)

    if sc == 'sc1':
        P_GFA_GT1 = (P_dem_GFA+P_ELH_GFA+P_GFA_to_GFB+P_GFA_to_GFC-P_WT_to_GFA)/no_GT_GFA

        if P_GFA_GT1<P_min_acc_LM25PE:
            P_GFA_GT1 = P_min_acc_LM25PE
        if no_GT_GFA > 1:
            P_GFA_GT2 = P_GFA_GT1
            if no_GT_GFA > 2:
                P_GFA_GT3 = P_GFA_GT2
                if no_GT_GFA > 3:
                    P_GFA_GT4 = P_GFA_GT3                    

        m_f_GFA_GT1, fuel_input_GFA_GT1, eff_GFA_GT1, TOT_GFA_GT1 =        LM25PE(model_MGT, P_GFA_GT1, T_amb, scaler=scaler_MGT)
        Q_max_GFA_GT1 = Q_max_LM25PE (P_GFA_GT1, TOT_GFA_GT1)     
        Q_max_GFA_GT2 = Q_max_GFA_GT1
        Q_max_GFA_GT3 = Q_max_GFA_GT1
        Q_max_GFA_GT4 = 0

        P_GFA_GTs = P_GFA_GT1+P_GFA_GT2+P_GFA_GT3+P_GFA_GT4


        if P_GFA_to_GFC < 0:
            P_positive = P_GFA_GTs - P_GFA_to_GFC + P_WT_to_GFA
            P_negative = P_dem_GFA + P_ELH_GFA + P_GFA_to_GFB
        else:
            P_positive = P_GFA_GTs + P_WT_to_GFA
            P_negative = P_dem_GFA + P_ELH_GFA + P_GFA_to_GFB + P_GFA_to_GFC


        P_imbalance_GFA = P_positive - P_negative



        if P_imbalance_GFA<0.001:
            P_imbalance_GFA = 0


        if P_imbalance_GFA >= 0:
            P_GFA_to_ELZ = P_imbalance_GFA
        else:
            print('Warning')
            print('P_imbalance_GFA:',P_imbalance_GFA)

        
    P_GFA_GT1 = np.ceil(P_GFA_GT1); P_GFA_GT2 = np.ceil(P_GFA_GT2); P_GFA_GT3 = np.ceil(P_GFA_GT3); P_GFA_GT4 = np.ceil(P_GFA_GT4)                  
    return P_GFA_GT1, P_GFA_GT2, P_GFA_GT3,  P_GFA_GT4, P_GFA_to_ELZ, P_ELH_GFA


# In[7]:


max_power_exach_electrolyzer = 0.05 # kW
max_num_of_electrolyzers = 4000

CO2_tax_per_tonne = 77 # EUR
high_coeff = 1000

# max_num_of_electrolyzers = 0

electricity_selling_factor = 0.8
electrical_heater_eff = 0.7

# electrolyzer_eff = 1
electrolyzer_efficiency = 0.7

# assumptions
el_price = 5e-5 # EUR/kJ
NG_price = 2e-6 # EUR/kJ

# assuming 90,000 EUR for AET100, and 25% of its value if we run it at full load 24/7
maximum_maint_cost_annu = 120000 * 35/100


maximum_maint_cost_daily = maximum_maint_cost_annu / 365 # EUR
maximum_maint_cost_hourly = maximum_maint_cost_daily/24

maximum_maint_cost_hourly = 1.73 # from G's paper
maximum_maint_cost_hourly = 0.1 # from G's paper


MGT_daily_prod_full_load = 24 * 3600 * 100 # kJ
NG_consum_MGT_daily_prod_full_load = 100/33 * MGT_daily_prod_full_load # kJ
NG_cost_MGT_daily_prod_full_load = NG_consum_MGT_daily_prod_full_load * NG_price
el_revenue_if_sell_all = MGT_daily_prod_full_load * el_price

real_eff_MGT = (el_revenue_if_sell_all - (NG_cost_MGT_daily_prod_full_load + maximum_maint_cost_daily))/(NG_cost_MGT_daily_prod_full_load + maximum_maint_cost_daily) * 100


# In[ ]:


# 1 Million BTU [MMBtu] = 293.071 070 172 22 Kilowatt hour [kWh]
# 1 kWh = 3600 kJ

mmBTU_to_kWh = 293.07107017222 
kWh_to_kJ = 3600



EperMWh_to_EperkJ = 1/3600000
P_req_H2_pro_per_gr = 5.5 * 3600/0.08988/1000 # kJ

rectifier_eff = 0.95
convertor_eff = 0.95


# In[ ]:


def span_data_to_actual_data(span_data, bounds):
    min_value, max_value = bounds
    return min_value + span_data * (max_value - min_value)


def x_span_fom_actual_data(actual_data, bounds):
    span_values = []
    for value, (min_value, max_value) in zip(actual_data, bounds):
        if max_value == min_value:
            span_values.append(0)
        else:
            span_values.append((value - min_value) / (max_value - min_value))
    return np.clip(np.array(span_values, dtype=float), 0, 1)


def initial_population_creator(x_initial, no_initial_pop, x_band):
    x_initial = np.asarray(x_initial, dtype=float)
    population = np.tile(x_initial, (int(no_initial_pop), 1))
    if len(population) > 1:
        population[1:] = np.random.uniform(0, 1, size=population[1:].shape)
    return population


def parameter_formater(parameter, digits):
    return np.round(parameter, digits)


def MG_parameter_boundary_def(opt_param_dict, optimization_window):
    x_band = []
    x_band_statements = []
    x_initial = []
    parameter_names = []

    for i in range(optimization_window):
        for param_name, (min_value, max_value, initial_value) in opt_param_dict.items():
            globals()[f"min_{param_name}"] = min_value
            globals()[f"max_{param_name}"] = max_value
            globals()[f"initial_{param_name}"] = initial_value

            bound_name = f"b_{param_name}_{i}"
            bound = [min_value, max_value]
            globals()[bound_name] = bound
            x_band.append(bound)
            x_band_statements.append(
                f"{bound_name} =[ min_{param_name}, max_{param_name}]"
            )

            x_initial.append(x_span_fom_actual_data([initial_value], [bound])[0])
            parameter_names.append(f"{param_name}_{i}")

    parameter_definition = ",".join(parameter_names) + "=x"
    no_initial_pop = 20 * len(x_initial)

    initial_pop = initial_population_creator(x_initial, no_initial_pop, x_band)

    return x_band, x_band_statements, parameter_definition, x_initial, no_initial_pop, initial_pop



# In[ ]:



def extract_x_span_for_initialization(df, x_band_statements):

    
    
    P_GFA_to_GFC_col = 'P_GFA_to_GFC [MW]'
    P_GFA_to_ELZ_col = 'P_GFA_to_ELZ [MW]'
    FR_GFA_GT1_col = 'FR_GFA_GT1 [-]'
    FR_GFA_GT2_col = 'FR_GFA_GT2 [-]'
    FR_GFA_GT3_col = 'FR_GFA_GT3 [-]'
    FR_GFA_GT4_col = 'FR_GFA_GT4 [-]'

    
    
    x_initial_span = []
    for param in range(len(x_band_statements)):
        

        exec(x_band_statements[param])
        name = x_band_statements[param].split('=')[0]
        
        no = int(name.split('_')[-1])

        bound = x_band_statements[param].split('=')[1]
        min_val =  eval(bound)[0]
        max_val =  eval(bound)[1]
        param_col_ = name[2:] # to remove the 'b_' from the begining
        
        param_col_ = param_col_.replace(param_col_.split('_')[-1], "col")
        param_col_ = eval(param_col_)
        current_value = df[param_col_].iloc[no]

        if max_val != min_val:
        
            current_value_span = (current_value-min_val)/(max_val-min_val)
        else:
            current_value_span = 1
        
        x_initial_span.append(current_value_span)

        
    return np.array(x_initial_span)


# In[13]:


from scipy.optimize import Bounds
from scipy.stats import qmc


# In[ ]:


def optimize_microgrid_performance(df_complete, parameter_definition, x_initial, x_band_statements,x_band_statements_all,initial_pop,H2_tank_initial,                          error_method='mae',display=None,constraints=None,actual_band=None, method='Nelder-Mead',max_itr=None,max_time=24*3600,display_step=500,buy=True,sell=True):
    
    try:
        if max_itr is None:
            max_itr = int(os.environ.get("OFFSHORE_MG_MAX_ITR", "20000"))

        if constraints is None:
            constraints = ()



        x_band = np.tile([0,1], (len(x_initial),1))

        for parameter_band_def in x_band_statements:
            exec(parameter_band_def, locals(), globals()) 

        global simulation_record
        global error_record
        global x_record
        


        def objective(x):


            
            spans = np.tile([0,1], (len(x_band),1))
            df_MG_round, cost_total, penalty_total = MG_run(df_complete, x, parameter_definition, H2_tank_initial,x_band_statements_all,buy=buy,sell=sell)
            Hy_balance_condition = [] # +1 if enough H2 is there to use, -1 if not

                    
            H2_reserved_for_nex_round = df_MG_round['H2_tank_aval [kg/s]'].iloc[-1] + df_MG_round['H2_tank_var [kg/s]'].iloc[-1] 
            
            
            if df_MG_round['P_GFA_GT1_dev [-]'].iloc[-1] > max_allowed_power_deviation:
                res_P_GFA_GT1_dev = penalty_power_deviations * floor(df_MG_round['P_GFA_GT1_dev [-]'].iloc[-1] - max_allowed_power_deviation)
            else:
                res_P_GFA_GT1_dev = 0
            if df_MG_round['P_GFA_GT2_dev [-]'].iloc[-1] > max_allowed_power_deviation:
                res_P_GFA_GT2_dev = penalty_power_deviations * floor(df_MG_round['P_GFA_GT2_dev [-]'].iloc[-1] - max_allowed_power_deviation)
            else:
                res_P_GFA_GT2_dev = 0        
            if df_MG_round['P_GFA_GT3_dev [-]'].iloc[-1] > max_allowed_power_deviation:
                res_P_GFA_GT3_dev = penalty_power_deviations * floor(df_MG_round['P_GFA_GT3_dev [-]'].iloc[-1] - max_allowed_power_deviation)
            else:
                res_P_GFA_GT3_dev = 0 
            if df_MG_round['P_GFA_GT4_dev [-]'].iloc[-1] > max_allowed_power_deviation:
                res_P_GFA_GT4_dev = penalty_power_deviations * floor(df_MG_round['P_GFA_GT4_dev [-]'].iloc[-1] - max_allowed_power_deviation)
            else:
                res_P_GFA_GT4_dev = 0                
                
            if df_MG_round['P_GFC_GT1_dev [-]'].iloc[-1] > max_allowed_power_deviation:
                res_P_GFC_GT1_dev = penalty_power_deviations * floor(df_MG_round['P_GFC_GT1_dev [-]'].iloc[-1] - max_allowed_power_deviation)
            else:
                res_P_GFC_GT1_dev = 0
            if df_MG_round['P_GFC_GT2_dev [-]'].iloc[-1] > max_allowed_power_deviation:
                res_P_GFC_GT2_dev = penalty_power_deviations * floor(df_MG_round['P_GFC_GT2_dev [-]'].iloc[-1] - max_allowed_power_deviation)
            else:
                res_P_GFC_GT2_dev = 0        
            if df_MG_round['P_GFC_GT3_dev [-]'].iloc[-1] > max_allowed_power_deviation:
                res_P_GFC_GT3_dev = penalty_power_deviations * floor(df_MG_round['P_GFC_GT3_dev [-]'].iloc[-1] - max_allowed_power_deviation)
            else:
                res_P_GFC_GT3_dev = 0 
                
            res_dev = res_P_GFA_GT1_dev+res_P_GFA_GT2_dev+res_P_GFA_GT3_dev+res_P_GFA_GT4_dev+res_P_GFC_GT1_dev+res_P_GFC_GT2_dev+res_P_GFC_GT3_dev  
                
            
            if sell:
                pass
            else:
                H2_reserve_incentive1 = (1* H2_reserved_for_nex_round *delta_t_time_step*LHV_H2* df_complete['NG_Price [EUR/MJ]'].iloc[-1])
                H2_reserve_incentive2 = (1* H2_reserved_for_nex_round *delta_t_time_step*LHV_H2/LHV_NG *  CO2_tax)
                H2_reserve_incentive = 0.5* ( H2_reserve_incentive1 + H2_reserve_incentive2)/len(df_complete)
            

            if H2_reserve_incentive>0:
            
                res7 = H2_reserve_incentive
            else:
                
                res7=0            
            exec('x_record[objective.count] = np.array(x)', locals(), globals())
            exec('simulation_record[objective.count] = df_MG_round')
            
            profit_tot = -cost_total -penalty_total + res7 - res_dev
    
    
    
            error = -profit_tot

            exec('error_record[objective.count] = error', locals(), globals())
            
                
            
            formatted_x = parameter_formater(x, 3)
            formatted_error = parameter_formater(error, 3)
            
            
            
            if objective.count%display_step == 0:
            
                print(' ')        
                print('>>>>>> itr = ', objective.count, ' cost = ', formatted_error) 
                print('Total cost:', parameter_formater(cost_total, 3))  
                print('Penalty cost:', parameter_formater(penalty_total, 3))  
                print('NOx emission cost:', parameter_formater(df_MG_round['cost_NOx_tax [EUR]'].sum(), 3))  
                print('H2 incentive:', parameter_formater(res7, 3))  
                print('Reserved H2 for the next round:', parameter_formater(df_MG_round['H2_tank_aval [kg/s]'].iloc[-1], 3)) 
                print('Deviations cost:', parameter_formater(res_dev, 3)) 
                print('Operation cost:', parameter_formater(df_MG_round['cost_total [EUR]'].sum(), 3))
                
            objective.count += 1

            del df_MG_round

            return error

        import warnings
        warnings.filterwarnings('ignore')
        

        x0 = x_initial
        no_initial_pop = 20 * len(x0)
        objective.count = 0
        max_opt_itr = 200
        max_x_itr = 10000 * no_initial_pop * max_opt_itr
        maxiter=50000

        xspan_record = np.empty((max_x_itr, len(x0)))
        x_record = np.empty((max_x_itr, len(x0)))
        error_record = np.empty(max_x_itr)
        simulation_record = dict()
        
        initial_pop = initial_population_creator(x_initial, no_initial_pop, x_band) 
        
        
        popsize = 20
        sampler = qmc.LatinHypercube(d=len(x_initial))
        sample = sampler.random(n=popsize)
        initial_pop = sample
        initial_pop[0] = x_initial

        tol = 0.001

        if max_itr <= 1:
            objective(np.asarray(x_initial, dtype=float))
        elif method=='ga':
            sol = differential_evolution(objective, x_band, args=(), strategy='best1bin',
                           maxiter=max(1, int(max_itr / max(popsize * len(x_initial), 1))), popsize=popsize, tol=tol,
                           mutation=(0.5, 1), recombination=0.7, seed=None,
                           callback=None, disp=True, polish=True,
                           init=initial_pop)

        elif method=='Nelder-Mead':

            sol = minimize(objective, x_initial, method='Nelder-Mead',tol=0.001,
                       options={'display': True, 'maxiter':max_itr, 'maxfev':max_itr}, bounds=x_band)  

        elif method=='L-BFGS-B':
            sol = minimize(objective, x_initial, method='L-BFGS-B',
                       constraints=constraints,
                       options={'display': True, 'maxiter':max_itr}, bounds=x_band, tol=0.0001)  

        error_record = error_record[0:len(simulation_record)] 
        iterations = np.arange(1, len(error_record)+1, 1)
        x_record = x_record[0:len(simulation_record)]  
        
        
        if display:
      
        

            simple_plotter(iterations, [error_record], x_label='Iteration',x_lim=[0, iterations[-1]+1], y_label='Cost Function', plot_title='Error',scatter=True)
            for x_no in range(len(x_initial)):
                param_name = parameter_definition.split(',')[x_no].split('=')[0]
                bound_lim = [min(x_band[x_no]), max(x_band[x_no])]
                bound_step = (bound_lim[1] - bound_lim[0])/10
                simple_plotter(iterations, [x_record[:,x_no]], x_label='Iteration', y_label='X'+str(x_no), y_lines=bound_lim, plot_title=param_name, y_lim=[bound_lim[0]-bound_step, bound_lim[1]+bound_step],scatter=True)
        
    except KeyboardInterrupt:
        error_record = error_record[0:len(simulation_record)] 
        iterations = np.arange(1, len(error_record)+1, 1)
        x_record = x_record[0:len(simulation_record)] 
        
         
        if display:
            error_record = error_record[0:len(simulation_record)] 
            iterations = np.arange(1, len(error_record)+1, 1)
            x_record = x_record[0:len(simulation_record)]         
        

            simple_plotter(iterations, [error_record], x_label='Iteration',x_lim=[0, iterations[-1]+1], y_label='Cost Function', plot_title='Error',scatter=True)
            for x_no in range(len(x_initial)):
                param_name = parameter_definition.split(',')[x_no].split('=')[0]
                bound_lim = [min(x_band[x_no]), max(x_band[x_no])]
                bound_step = (bound_lim[1] - bound_lim[0])/10
                simple_plotter(iterations, [x_record[:,x_no]], x_label='Iteration', y_label='X'+str(x_no), y_lines=bound_lim, plot_title=param_name, y_lim=[bound_lim[0]-bound_step, bound_lim[1]+bound_step],scatter=True)
        
        
        
        print('>>>>>>>>>>>>> The optimization is intrrupted by the user')
    
    print('>>>>>>>>>>>>> The optimization is finished.')
    return simulation_record, x_record, error_record


# In[ ]:


def set_zero_list(param):
    param = []
    return param


# In[ ]:


def constr_f(x):
    exec(parameter_definition, locals(), globals())     
    
    
    df_MG_round, cost_balance_vector = MG_run(df, x, rserve_H2)

    Hy_balance_condition = [] # +1 if enough H2 is there to use, -1 if not

    for row in range(len(df_MG_round)):
        Tank_content_up_to_previous_step = df_MG_round['H2_tank_aval [g/s]'].iloc[row]
        
#         A = df_MG_round['m_f_MGT_H2 [g/s]'].iloc[row] * delta_t_time_step

        balance = Tank_content_up_to_previous_step-df_MG_round['m_f_MGT_H2 [g/s]'].iloc[row]
        
        if (df_MG_round['m_f_MGT_H2 [g/s]'].iloc[row] <= Tank_content_up_to_previous_step):
            Hy_balance_condition.append(1)
        else:
            Hy_balance_condition.append(0)
    res = np.prod(np.array(Hy_balance_condition))
    
    return res


# In[ ]:


def geo_distance(x,y,x0,y0):

    distance_from_target = np.sqrt((x-x0)**2 + (y-y0)**2)
    return distance_from_target


# In[ ]:


def find_nearest(X, value):
    index = np.unravel_index(np.argmin(np.abs(X - value)), X.shape)
    return index, X[index]
