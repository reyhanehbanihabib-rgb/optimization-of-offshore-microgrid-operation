#!/usr/bin/env python
# coding: utf-8


import joblib
import keras
import numpy as np
from src.paths import MGT_MODEL_DIR, require_path

# In[ ]:



# Micro gas turbine
scaler_MGT = joblib.load(require_path(MGT_MODEL_DIR / 'model1_scaler.save'))
model_MGT = keras.models.load_model(require_path(MGT_MODEL_DIR / 'model1.h5'))
input_parameters_MGT = ['P_ref [kW]', 'T1 [degC]']
output_parameters_MGT = ['m_f [gr/s]', 'TOT [degC]', 'N_act [rpm]', 'P_act [kW]']


# In[ ]:





def GFA_operation_Opt(T_amb, P_dem_GFA, Q_dem_GFA, FR_GFA_GT1, FR_GFA_GT2, FR_GFA_GT3, FR_GFA_GT4, H2_available, Pr_NG,delta_t):
    
    T_amb, P_dem_GFA, Q_dem_GFA, FR_GFA_GT1, FR_GFA_GT2, FR_GFA_GT3, FR_GFA_GT4, H2_available, Pr_NG,delta_t = [round(num, 2) for num in [T_amb, P_dem_GFA, Q_dem_GFA, FR_GFA_GT1, FR_GFA_GT2, FR_GFA_GT3, FR_GFA_GT4, H2_available, Pr_NG,delta_t]]

    
    
    
    min_P_GT = 9
    max_P_GT = 23
    
    impossibility_cost = 0
    P_ELH_GFA = 0
    

    Q_and_P_const = GFA_operation_df[(GFA_operation_df['T_amb_GFA [degC]']<=T_amb+0.5)&
                    (GFA_operation_df['T_amb_GFA [degC]']>=T_amb-0.5)&
                    (GFA_operation_df['P_GFA_GTs_total [MW]']<=P_dem_GFA+1)&
                    (GFA_operation_df['P_GFA_GTs_total [MW]']>=P_dem_GFA+0.0001)&                
                    (GFA_operation_df['Q_max_GFA_GTs_total [MW]']>=Q_dem_GFA+0.0001)]

    if len(Q_and_P_const) == 0:

        P_const = GFA_operation_df[(GFA_operation_df['T_amb_GFA [degC]']<=T_amb+0.5)&
                        (GFA_operation_df['T_amb_GFA [degC]']>=T_amb-0.5)&
                        (GFA_operation_df['P_GFA_GTs_total [MW]']<=P_dem_GFA+1)&
                        (GFA_operation_df['P_GFA_GTs_total [MW]']>=P_dem_GFA+0.0001)]

        max_Q_available = P_const['Q_max_GFA_GTs_total [MW]'].max()
        P_ELH_GFA = (Q_dem_GFA-max_Q_available)/electrical_heater_eff
        Q_and_P_const = GFA_operation_df[(GFA_operation_df['T_amb_GFA [degC]']<=T_amb+0.5)&
                        (GFA_operation_df['T_amb_GFA [degC]']>=T_amb-0.5)&
                        (GFA_operation_df['P_GFA_GTs_total [MW]']<=P_dem_GFA+P_ELH_GFA+2)&
                        (GFA_operation_df['P_GFA_GTs_total [MW]']>=P_dem_GFA+P_ELH_GFA+0.001)&
                        (GFA_operation_df['Q_max_GFA_GTs_total [MW]']>=max_Q_available)]
        if len(Q_and_P_const) == 0: # Maybe the power demand is so low that does not turn on any GTs.
#             if P_dem_GFA<min_P_GT:
                Q_dem_GFA_mod = Q_dem_GFA
                while (len(Q_and_P_const) == 0)& (Q_dem_GFA_mod>=0):
                    max_Q_available = P_const['Q_max_GFA_GTs_total [MW]'].max()
                    P_ELH_GFA = (Q_dem_GFA-Q_dem_GFA_mod)/electrical_heater_eff
                    Q_and_P_const = GFA_operation_df[(GFA_operation_df['T_amb_GFA [degC]']<=T_amb+0.5)&
                                    (GFA_operation_df['T_amb_GFA [degC]']>=T_amb-0.5)&
                                    (GFA_operation_df['P_GFA_GTs_total [MW]']<=P_dem_GFA+P_ELH_GFA+2)&
                                    (GFA_operation_df['P_GFA_GTs_total [MW]']>=P_dem_GFA+P_ELH_GFA+0.0001)&
                                    (GFA_operation_df['Q_max_GFA_GTs_total [MW]']>=Q_dem_GFA_mod)]                    
                    Q_dem_GFA_mod = Q_dem_GFA_mod - 1

    no_options = len(Q_and_P_const)  

    if no_options > 0:
        Q_and_P_const = Q_and_P_const.reset_index(drop=True)
         
        if H2_available<0:
            H2_available = 0
        
        
        
        
        fuel_input_NG_GFA_GT1 = FR_GFA_GT1 * Q_and_P_const['fuel_input_GFA_GT1 [MW]']; m_f_NG_GFA_GT1 = fuel_input_NG_GFA_GT1/LHV_NG
        fuel_input_H2_GFA_GT1 = (1-FR_GFA_GT1) * Q_and_P_const['fuel_input_GFA_GT1 [MW]']; m_f_H2_GFA_GT1 = fuel_input_H2_GFA_GT1/LHV_H2 
        fuel_input_NG_GFA_GT2 = FR_GFA_GT2 * Q_and_P_const['fuel_input_GFA_GT2 [MW]']; m_f_NG_GFA_GT2 = fuel_input_NG_GFA_GT2/LHV_NG
        fuel_input_H2_GFA_GT2 = (1-FR_GFA_GT2) * Q_and_P_const['fuel_input_GFA_GT2 [MW]']; m_f_H2_GFA_GT2 = fuel_input_H2_GFA_GT2/LHV_H2 
        fuel_input_NG_GFA_GT3 = FR_GFA_GT3 * Q_and_P_const['fuel_input_GFA_GT3 [MW]']; m_f_NG_GFA_GT3 = fuel_input_NG_GFA_GT3/LHV_NG
        fuel_input_H2_GFA_GT3 = (1-FR_GFA_GT3) * Q_and_P_const['fuel_input_GFA_GT3 [MW]']; m_f_H2_GFA_GT3 = fuel_input_H2_GFA_GT3/LHV_H2 
        fuel_input_NG_GFA_GT4 = FR_GFA_GT4 * Q_and_P_const['fuel_input_GFA_GT4 [MW]']; m_f_NG_GFA_GT4 = fuel_input_NG_GFA_GT4/LHV_NG
        fuel_input_H2_GFA_GT4 = (1-FR_GFA_GT4) * Q_and_P_const['fuel_input_GFA_GT4 [MW]']; m_f_H2_GFA_GT4 = fuel_input_H2_GFA_GT4/LHV_H2 

        
        
        
        fuel_input_H2_GFA_GTs = fuel_input_H2_GFA_GT1+fuel_input_H2_GFA_GT2+fuel_input_H2_GFA_GT3+fuel_input_H2_GFA_GT4
        corr_factor = H2_available * LHV_H2/fuel_input_H2_GFA_GTs
        
        corr_factor = corr_factor.clip(upper=1)
        corr_factor = corr_factor.replace([0, np.inf], 0)
        corr_factor = corr_factor.replace([0, np.nan], 0)
        

        fuel_input_H2_GFA_GT1 =corr_factor * (1-FR_GFA_GT1) * Q_and_P_const['fuel_input_GFA_GT1 [MW]']; m_f_H2_GFA_GT1 = fuel_input_H2_GFA_GT1/LHV_H2 
        fuel_input_NG_GFA_GT1 = Q_and_P_const['fuel_input_GFA_GT1 [MW]']-fuel_input_H2_GFA_GT1; m_f_NG_GFA_GT1 = fuel_input_NG_GFA_GT1/LHV_NG
        fuel_input_H2_GFA_GT2 =corr_factor * (1-FR_GFA_GT2) * Q_and_P_const['fuel_input_GFA_GT2 [MW]']; m_f_H2_GFA_GT2 = fuel_input_H2_GFA_GT2/LHV_H2 
        fuel_input_NG_GFA_GT2 = Q_and_P_const['fuel_input_GFA_GT2 [MW]']-fuel_input_H2_GFA_GT2; m_f_NG_GFA_GT2 = fuel_input_NG_GFA_GT2/LHV_NG
        fuel_input_H2_GFA_GT3 =corr_factor * (1-FR_GFA_GT3) * Q_and_P_const['fuel_input_GFA_GT3 [MW]']; m_f_H2_GFA_GT3 = fuel_input_H2_GFA_GT3/LHV_H2 
        fuel_input_NG_GFA_GT3 = Q_and_P_const['fuel_input_GFA_GT3 [MW]']-fuel_input_H2_GFA_GT3; m_f_NG_GFA_GT3 = fuel_input_NG_GFA_GT3/LHV_NG
        fuel_input_H2_GFA_GT4 =corr_factor * (1-FR_GFA_GT4) * Q_and_P_const['fuel_input_GFA_GT4 [MW]']; m_f_H2_GFA_GT4 = fuel_input_H2_GFA_GT4/LHV_H2 
        fuel_input_NG_GFA_GT4 = Q_and_P_const['fuel_input_GFA_GT4 [MW]']-fuel_input_H2_GFA_GT4; m_f_NG_GFA_GT4 = fuel_input_NG_GFA_GT4/LHV_NG
        
        cost_MNT_GFA_GT1 = LM25PE_MNT_cost_(Q_and_P_const['P_GFA_GT1 [MW]'])
        cost_MNT_GFA_GT2 = LM25PE_MNT_cost_(Q_and_P_const['P_GFA_GT2 [MW]'])
        cost_MNT_GFA_GT3 = LM25PE_MNT_cost_(Q_and_P_const['P_GFA_GT3 [MW]'])
        cost_MNT_GFA_GT4 = LM25PE_MNT_cost_(Q_and_P_const['P_GFA_GT4 [MW]'])
        
        cost_MNT_GT_total_GFA = cost_MNT_GFA_GT1 + cost_MNT_GFA_GT2 + cost_MNT_GFA_GT3 + cost_MNT_GFA_GT4


        m_f_NG_total_GFA = m_f_NG_GFA_GT1 + m_f_NG_GFA_GT2 + m_f_NG_GFA_GT3 + m_f_NG_GFA_GT4

        
        
        NOx_GFA_GT1 = NOx_produced(Q_and_P_const['P_GFA_GT1 [MW]']) 
        NOx_GFA_GT2 = NOx_produced(Q_and_P_const['P_GFA_GT2 [MW]']) 
        NOx_GFA_GT3 = NOx_produced(Q_and_P_const['P_GFA_GT3 [MW]']) 
        NOx_GFA_GT4 = NOx_produced(Q_and_P_const['P_GFA_GT4 [MW]']) 

        
        
        cost_NOx_tax_GFA = (NOx_GFA_GT1+NOx_GFA_GT2+NOx_GFA_GT3+NOx_GFA_GT4)*NOx_tax/10 * delta_t # EUR, 10 is to change NOK to EUR
                
        

        cost_NG_GFA = m_f_NG_total_GFA * Pr_NG * delta_t  # EUR

        cost_NG_tax_GFA  = CO2_tax * m_f_NG_total_GFA * delta_t
        

        cost_total_GFA = cost_NG_GFA + cost_NG_tax_GFA + cost_MNT_GT_total_GFA + cost_NOx_tax_GFA
        
        cost_total_GFA = cost_total_GFA.dropna()
        min_index = cost_total_GFA.idxmin()
#         print(cost_total_GFA)
#         print(min_index)
        fuel_input_NG_GFA_GT1=fuel_input_NG_GFA_GT1[min_index];m_f_NG_GFA_GT1=m_f_NG_GFA_GT1[min_index]
        fuel_input_H2_GFA_GT1=fuel_input_H2_GFA_GT1[min_index];m_f_H2_GFA_GT1=m_f_H2_GFA_GT1[min_index]
        fuel_input_NG_GFA_GT2=fuel_input_NG_GFA_GT2[min_index];m_f_NG_GFA_GT2=m_f_NG_GFA_GT2[min_index]
        fuel_input_H2_GFA_GT2=fuel_input_H2_GFA_GT2[min_index];m_f_H2_GFA_GT2=m_f_H2_GFA_GT2[min_index]
        fuel_input_NG_GFA_GT3=fuel_input_NG_GFA_GT3[min_index];m_f_NG_GFA_GT3=m_f_NG_GFA_GT3[min_index]
        fuel_input_H2_GFA_GT3=fuel_input_H2_GFA_GT3[min_index];m_f_H2_GFA_GT3=m_f_H2_GFA_GT3[min_index]
        fuel_input_NG_GFA_GT4=fuel_input_NG_GFA_GT4[min_index];m_f_NG_GFA_GT4=m_f_NG_GFA_GT4[min_index]
        fuel_input_H2_GFA_GT4=fuel_input_H2_GFA_GT4[min_index];m_f_H2_GFA_GT4=m_f_H2_GFA_GT4[min_index]
        
        
        m_f_NG_total_GFA = m_f_NG_GFA_GT1 + m_f_NG_GFA_GT2 + m_f_NG_GFA_GT3 + m_f_NG_GFA_GT4
        m_f_H2_total_GFA = m_f_H2_GFA_GT1 + m_f_H2_GFA_GT2 + m_f_H2_GFA_GT3 + m_f_H2_GFA_GT4 



        cost_NG_GFA=cost_NG_GFA[min_index];
        cost_NG_tax_GFA=cost_NG_tax_GFA[min_index]
        cost_MNT_GT_total_GFA=cost_MNT_GT_total_GFA[min_index]
        cost_NOx_tax_GFA=cost_NOx_tax_GFA[min_index]
        cost_total_GFA=cost_total_GFA[min_index] 

        P_GFA_GT1 = Q_and_P_const['P_GFA_GT1 [MW]'].loc[min_index]
        P_GFA_GT2 = Q_and_P_const['P_GFA_GT2 [MW]'].loc[min_index]
        P_GFA_GT3 = Q_and_P_const['P_GFA_GT3 [MW]'].loc[min_index]
        P_GFA_GT4 = Q_and_P_const['P_GFA_GT4 [MW]'].loc[min_index]
        P_GFA_GTs_total = Q_and_P_const['P_GFA_GTs_total [MW]'].loc[min_index]

        Q_max_GFA_GT1 = Q_and_P_const['Q_max_GFA_GT1 [MW]'].loc[min_index]
        Q_max_GFA_GT2 = Q_and_P_const['Q_max_GFA_GT2 [MW]'].loc[min_index]
        Q_max_GFA_GT3 = Q_and_P_const['Q_max_GFA_GT3 [MW]'].loc[min_index]
        Q_max_GFA_GT4 = Q_and_P_const['Q_max_GFA_GT4 [MW]'].loc[min_index]
        Q_max_GFA_GTs_total = Q_and_P_const['Q_max_GFA_GTs_total [MW]'].loc[min_index]


        fuel_input_GFA_GT1 = Q_and_P_const['fuel_input_GFA_GT1 [MW]'].loc[min_index]
        fuel_input_GFA_GT2 = Q_and_P_const['fuel_input_GFA_GT2 [MW]'].loc[min_index]
        fuel_input_GFA_GT3 = Q_and_P_const['fuel_input_GFA_GT3 [MW]'].loc[min_index]
        fuel_input_GFA_GT4 = Q_and_P_const['fuel_input_GFA_GT4 [MW]'].loc[min_index]
        optimum_GFA = [P_GFA_GT1,P_GFA_GT2,P_GFA_GT3,P_GFA_GT4,P_GFA_GTs_total,P_ELH_GFA,
                      Q_max_GFA_GT1,Q_max_GFA_GT2,Q_max_GFA_GT3,Q_max_GFA_GT4,Q_max_GFA_GTs_total,
                      fuel_input_GFA_GT1,fuel_input_GFA_GT2,fuel_input_GFA_GT3,fuel_input_GFA_GT4,
                      fuel_input_NG_GFA_GT1,fuel_input_H2_GFA_GT1,
                      fuel_input_NG_GFA_GT2,fuel_input_H2_GFA_GT2,
                      fuel_input_NG_GFA_GT3,fuel_input_H2_GFA_GT3,
                      fuel_input_NG_GFA_GT4,fuel_input_H2_GFA_GT4,
                      m_f_NG_GFA_GT1,m_f_NG_GFA_GT2,m_f_NG_GFA_GT3,m_f_NG_GFA_GT4,
                      m_f_H2_GFA_GT1,m_f_H2_GFA_GT2,m_f_H2_GFA_GT3,m_f_H2_GFA_GT4,
                      m_f_NG_total_GFA,m_f_H2_total_GFA,
                      cost_NG_GFA,cost_NG_tax_GFA,cost_NOx_tax_GFA,cost_MNT_GT_total_GFA,cost_total_GFA
                      ]
        output_cost = cost_total_GFA
    else:
        impossibility_cost = 1e5;
        
#         print('Warning! There is no match!')

        output_cost = impossibility_cost
        optimum_GFA = np.zeros(38)

    return impossibility_cost,optimum_GFA


# In[ ]:





def GFC_operation_Opt(T_amb, P_dem_GFC, Q_dem_GFC, FR_GFC_GT1, FR_GFC_GT2, FR_GFC_GT3, Pr_NG,delta_t):
    T_amb, P_dem_GFC, Q_dem_GFC, FR_GFC_GT1, FR_GFC_GT2, FR_GFC_GT3, Pr_NG,delta_t = [round(num, 2) for num in [T_amb, P_dem_GFC, Q_dem_GFC, FR_GFC_GT1, FR_GFC_GT2, FR_GFC_GT3, Pr_NG,delta_t]]
    
    
    min_P_GT = 9
    max_P_GT = 23    
    impossibility_cost = 0
    P_ELH_GFC = 0

    Q_and_P_const = GFC_operation_df[(GFC_operation_df['T_amb_GFC [degC]']<=T_amb+0.5)&
                    (GFC_operation_df['T_amb_GFC [degC]']>=T_amb-0.5)&
                    (GFC_operation_df['P_GFC_GTs_total [MW]']<=P_dem_GFC+1)&
                    (GFC_operation_df['P_GFC_GTs_total [MW]']>=P_dem_GFC+0.0001)&                
                    (GFC_operation_df['Q_max_GFC_GTs_total [MW]']>=Q_dem_GFC+0.0001)]

    if len(Q_and_P_const) == 0:
        P_const = GFC_operation_df[(GFC_operation_df['T_amb_GFC [degC]']<=T_amb+0.5)&
                        (GFC_operation_df['T_amb_GFC [degC]']>=T_amb-0.5)&
                        (GFC_operation_df['P_GFC_GTs_total [MW]']<=P_dem_GFC+1)&
                        (GFC_operation_df['P_GFC_GTs_total [MW]']>=P_dem_GFC+0.0001)]
        
        

        max_Q_available = P_const['Q_max_GFC_GTs_total [MW]'].max()
        P_ELH_GFC = (Q_dem_GFC-max_Q_available)/electrical_heater_eff
        Q_and_P_const = GFC_operation_df[(GFC_operation_df['T_amb_GFC [degC]']<=T_amb+0.5)&
                        (GFC_operation_df['T_amb_GFC [degC]']>=T_amb-0.5)&
                        (GFC_operation_df['P_GFC_GTs_total [MW]']<=P_dem_GFC+P_ELH_GFC+2)&
                        (GFC_operation_df['P_GFC_GTs_total [MW]']>=P_dem_GFC+P_ELH_GFC+0.0001)&
                        (GFC_operation_df['Q_max_GFC_GTs_total [MW]']>=max_Q_available)]
        if len(Q_and_P_const) == 0: # Maybe the power demand is so low that does not turn on any GTs.
#             if P_dem_GFC<min_P_GT:
                Q_dem_GFC_mod = Q_dem_GFC
                while (len(Q_and_P_const) == 0)& (Q_dem_GFC_mod>=0):
                    max_Q_available = P_const['Q_max_GFC_GTs_total [MW]'].max()
                    P_ELH_GFC = (Q_dem_GFC-Q_dem_GFC_mod)/electrical_heater_eff
                    Q_and_P_const = GFC_operation_df[(GFC_operation_df['T_amb_GFC [degC]']<=T_amb+0.5)&
                                    (GFC_operation_df['T_amb_GFC [degC]']>=T_amb-0.5)&
                                    (GFC_operation_df['P_GFC_GTs_total [MW]']<=P_dem_GFC+P_ELH_GFC+2)&
                                    (GFC_operation_df['P_GFC_GTs_total [MW]']>=P_dem_GFC+P_ELH_GFC+0.0001)&
                                    (GFC_operation_df['Q_max_GFC_GTs_total [MW]']>=Q_dem_GFC_mod)]                    
                    Q_dem_GFC_mod = Q_dem_GFC_mod - 1
#             print('P_dem_GFC+P_ELH_GFC:',P_dem_GFC+P_ELH_GFC)
#             print('Q_dem_GFC_mod:',Q_dem_GFC_mod)
            
#             display(Q_and_P_const)
            
            


    no_options = len(Q_and_P_const)  

#     Q_and_P_const = Q_and_P_const.reset_index(drop=True)
    if no_options > 0:
        Q_and_P_const = Q_and_P_const.reset_index(drop=True)
    
        fuel_input_NG_GFC_GT1 = FR_GFC_GT1 * Q_and_P_const['fuel_input_GFC_GT1 [MW]']; m_f_NG_GFC_GT1 = fuel_input_NG_GFC_GT1/LHV_NG
        fuel_input_H2_GFC_GT1 = (1-FR_GFC_GT1) * Q_and_P_const['fuel_input_GFC_GT1 [MW]']; m_f_H2_GFC_GT1 = fuel_input_H2_GFC_GT1/LHV_H2 
        fuel_input_NG_GFC_GT2 = FR_GFC_GT2 * Q_and_P_const['fuel_input_GFC_GT2 [MW]']; m_f_NG_GFC_GT2 = fuel_input_NG_GFC_GT2/LHV_NG
        fuel_input_H2_GFC_GT2 = (1-FR_GFC_GT2) * Q_and_P_const['fuel_input_GFC_GT2 [MW]']; m_f_H2_GFC_GT2 = fuel_input_H2_GFC_GT2/LHV_H2 
        fuel_input_NG_GFC_GT3 = FR_GFC_GT3 * Q_and_P_const['fuel_input_GFC_GT3 [MW]']; m_f_NG_GFC_GT3 = fuel_input_NG_GFC_GT3/LHV_NG
        fuel_input_H2_GFC_GT3 = (1-FR_GFC_GT3) * Q_and_P_const['fuel_input_GFC_GT3 [MW]']; m_f_H2_GFC_GT3 = fuel_input_H2_GFC_GT3/LHV_H2 



        cost_MNT_GFC_GT1 = LM25PE_MNT_cost_(Q_and_P_const['P_GFC_GT1 [MW]'])
        cost_MNT_GFC_GT2 = LM25PE_MNT_cost_(Q_and_P_const['P_GFC_GT2 [MW]'])
        cost_MNT_GFC_GT3 = LM25PE_MNT_cost_(Q_and_P_const['P_GFC_GT3 [MW]'])

        cost_MNT_GT_total_GFC = cost_MNT_GFC_GT1 + cost_MNT_GFC_GT2 + cost_MNT_GFC_GT3


        m_f_NG_total_GFC = m_f_NG_GFC_GT1 + m_f_NG_GFC_GT2 + m_f_NG_GFC_GT3 
        
        
        
        NOx_GFC_GT1 = NOx_produced(Q_and_P_const['P_GFC_GT1 [MW]']) 
        NOx_GFC_GT2 = NOx_produced(Q_and_P_const['P_GFC_GT2 [MW]']) 
        NOx_GFC_GT3 = NOx_produced(Q_and_P_const['P_GFC_GT3 [MW]']) 

        cost_NOx_tax_GFC = (NOx_GFC_GT1+NOx_GFC_GT2+NOx_GFC_GT3)*NOx_tax/10 * delta_t # EUR, 10 is to change NOK to EUR
                
        
        cost_NG_GFC = m_f_NG_total_GFC * Pr_NG * delta_t  # EUR

        cost_NG_tax_GFC  = CO2_tax * m_f_NG_total_GFC * delta_t

        cost_total_GFC = cost_NG_GFC + cost_NG_tax_GFC + cost_MNT_GT_total_GFC  + cost_NOx_tax_GFC
        min_index = cost_total_GFC.idxmin()

        fuel_input_NG_GFC_GT1=fuel_input_NG_GFC_GT1[min_index];m_f_NG_GFC_GT1=m_f_NG_GFC_GT1[min_index]
        fuel_input_H2_GFC_GT1=fuel_input_H2_GFC_GT1[min_index];m_f_H2_GFC_GT1=m_f_H2_GFC_GT1[min_index]
        fuel_input_NG_GFC_GT2=fuel_input_NG_GFC_GT2[min_index];m_f_NG_GFC_GT2=m_f_NG_GFC_GT2[min_index]
        fuel_input_H2_GFC_GT2=fuel_input_H2_GFC_GT2[min_index];m_f_H2_GFC_GT2=m_f_H2_GFC_GT2[min_index]
        fuel_input_NG_GFC_GT3=fuel_input_NG_GFC_GT3[min_index];m_f_NG_GFC_GT3=m_f_NG_GFC_GT3[min_index]
        fuel_input_H2_GFC_GT3=fuel_input_H2_GFC_GT3[min_index];m_f_H2_GFC_GT3=m_f_H2_GFC_GT3[min_index]
        m_f_NG_total_GFC = m_f_NG_GFC_GT1 + m_f_NG_GFC_GT2 + m_f_NG_GFC_GT3 
        m_f_H2_total_GFC = m_f_H2_GFC_GT1 + m_f_H2_GFC_GT2 + m_f_H2_GFC_GT3 

        # cost_MNT_GFC_GT1 = cost_MNT_GFC_GT1[min_index]; cost_MNT_GFC_GT2 = cost_MNT_GFC_GT2[min_index]; cost_MNT_GFC_GT3 = cost_MNT_GFC_GT3[min_index]

        
        cost_NG_GFC=cost_NG_GFC[min_index];
        cost_NG_tax_GFC=cost_NG_tax_GFC[min_index]
        cost_MNT_GT_total_GFC=cost_MNT_GT_total_GFC[min_index]
        cost_NOx_tax_GFC=cost_NOx_tax_GFC[min_index]
        cost_total_GFC=cost_total_GFC[min_index]
        

        P_GFC_GT1 = Q_and_P_const['P_GFC_GT1 [MW]'].loc[min_index]
        P_GFC_GT2 = Q_and_P_const['P_GFC_GT2 [MW]'].loc[min_index]
        P_GFC_GT3 = Q_and_P_const['P_GFC_GT3 [MW]'].loc[min_index]
        P_GFC_GTs_total = Q_and_P_const['P_GFC_GTs_total [MW]'].loc[min_index]

        Q_max_GFC_GT1 = Q_and_P_const['Q_max_GFC_GT1 [MW]'].loc[min_index]
        Q_max_GFC_GT2 = Q_and_P_const['Q_max_GFC_GT2 [MW]'].loc[min_index]
        Q_max_GFC_GT3 = Q_and_P_const['Q_max_GFC_GT3 [MW]'].loc[min_index]
        Q_max_GFC_GTs_total = Q_and_P_const['Q_max_GFC_GTs_total [MW]'].loc[min_index]


        fuel_input_GFC_GT1 = Q_and_P_const['fuel_input_GFC_GT1 [MW]'].loc[min_index]
        fuel_input_GFC_GT2 = Q_and_P_const['fuel_input_GFC_GT2 [MW]'].loc[min_index]
        fuel_input_GFC_GT3 = Q_and_P_const['fuel_input_GFC_GT3 [MW]'].loc[min_index]
        optimum_GFC = [P_GFC_GT1,P_GFC_GT2,P_GFC_GT3,P_GFC_GTs_total,P_ELH_GFC,
                      Q_max_GFC_GT1,Q_max_GFC_GT2,Q_max_GFC_GT3,Q_max_GFC_GTs_total,
                      fuel_input_GFC_GT1,fuel_input_GFC_GT2,fuel_input_GFC_GT3,
                      fuel_input_NG_GFC_GT1,fuel_input_H2_GFC_GT1,
                      fuel_input_NG_GFC_GT2,fuel_input_H2_GFC_GT2,
                      fuel_input_NG_GFC_GT3,fuel_input_H2_GFC_GT3,
                      m_f_NG_GFC_GT1,m_f_NG_GFC_GT2,m_f_NG_GFC_GT3,
                      m_f_H2_GFC_GT1,m_f_H2_GFC_GT2,m_f_H2_GFC_GT3,
                      m_f_NG_total_GFC,m_f_H2_total_GFC,
                      cost_NG_GFC,cost_NG_tax_GFC,cost_NOx_tax_GFC,cost_MNT_GT_total_GFC,cost_total_GFC
                      ]
        output_cost = cost_total_GFC
    else:
        impossibility_cost = 1e5;
        
#         print('Warning! There is no match!')

        output_cost = impossibility_cost
        optimum_GFC = np.zeros(31)
        

    return impossibility_cost,optimum_GFC
