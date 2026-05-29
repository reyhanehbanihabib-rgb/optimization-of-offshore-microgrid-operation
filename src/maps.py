#!/usr/bin/env python
# coding: utf-8
import pandas as pd



import joblib
from keras.models import load_model
import numpy as np
import math
from src.paths import DATA_ROOT, require_path

turbine_map_eta_scaler = joblib.load(require_path(DATA_ROOT / 'turbine_map_scaler_eta.save'))
turbine_map_eta_ann_model = load_model(require_path(DATA_ROOT / 'ANN_model_turbine_map_2_layers_eta.h5'))

turbine_map_pr_scaler = joblib.load(require_path(DATA_ROOT / 'turbine_map_scaler.save'))
turbine_map_pr_ann_model = load_model(require_path(DATA_ROOT / 'ANN_model_turbine_map_2_layers.h5'))




compressor_map_eta_scaler = joblib.load(require_path(DATA_ROOT / 'compressor_map_scaler_eta.save'))
compressor_map_eta_ann_model = load_model(require_path(DATA_ROOT / 'ETA.h5'))

compressor_map_pr_scaler = joblib.load(require_path(DATA_ROOT / 'compressor_map_scaler_pr.save'))
compressor_map_pr_ann_model = load_model(require_path(DATA_ROOT / 'PR.h5'))




# In[34]:


def intake_map(intake_dp_coeff_factor, intake_dT_coeff_factor, intake_dT_intercept_factor):
    # design values extracted from Volvo
    mdot_des = 0.7759
    p1_des = 101325
    p2_des = 99140
#     T1_des = 291.15
    T1_des = 29115 # the above value is correct but it is tunned with this value
    
    dT_coeff_intake_des = 0.11038331 # based on linear regression fit to PSI data
    dT_intercept_intake_des = - 0.3108407786806583 # based on linear regression fit to PSI data
    mdot_corr_des = (mdot_des * math.sqrt(T1_des))/p1_des
    dp_des = p1_des - p2_des
    dp_coeff_intake = intake_dp_coeff_factor * (dp_des/mdot_corr_des)
    dT_coeff_intake = intake_dT_coeff_factor * dT_coeff_intake_des
    dT_intercept_intake = intake_dT_intercept_factor * dT_intercept_intake_des

    return dp_coeff_intake, dT_coeff_intake, dT_intercept_intake



import joblib
from keras.models import load_model
import numpy as np
import math

# for ANN model with turbine map
def compressor_map(comp_area_in_factor, comp_area_out_factor, comp_m_factor, comp_eff_factor):
    area_A_C = comp_area_in_factor * 0.01
    area_B_C = comp_area_out_factor * 0.01
    return comp_m_factor, comp_eff_factor, area_A_C, area_B_C



import joblib
from keras.models import load_model
import numpy as np
import math

def compressor_map_df_builder(comp_area_in_factor, comp_area_out_factor, comp_m_factor, comp_eff_factor):

    area_A_C = comp_area_in_factor * 0.01
    area_B_C = comp_area_out_factor * 0.01    
    ################# Compressor characteristics ###############
    ################# Corrected speed N[rpm]/sqrt(T[K])
    nrott = [1268.4, 2114.2, 2537.0, 2959.8, 3382.6, 3805.4, 4016.9, 4228.3, 4439.7, 4651.1, 4862.5];
    ################# Beta lines ###########################################
    beta_c = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25];
    ################# Compressor corrected air flow [kg/s]*[K]/[bar] ##########
    cairvolvo_comp = comp_m_factor * 1e5 *    np.array([    [0.000011167, 0.000013958, 0.000016746, 0.000019313, 0.000021881, 0.000024449, 0.000027016, 0.000029598, 0.000032166, 0.000034733, 0.000037301, 0.000039869, 0.000042436, 0.000042436, 0.000042436, 0.000042436],    [0.000023023, 0.000026512, 0.000030003, 0.000032626, 0.00003525, 0.000037873, 0.000040497, 0.00004312, 0.00004573, 0.000048353, 0.000050977, 0.0000536, 0.000056224, 0.000056224, 0.000056224, 0.000056224],    [0.000032096, 0.000036282, 0.000040469, 0.00004312, 0.000045786, 0.000048437, 0.000051088, 0.000053754, 0.000056405, 0.000059057, 0.000061708, 0.000064373, 0.000067025, 0.000067025, 0.000067025, 0.000067025],    [0.000047446, 0.00005233, 0.000055819, 0.000058359, 0.000060899, 0.000063452, 0.000065992, 0.000068532, 0.000071072, 0.000073611, 0.000076165, 0.000078705, 0.000081245, 0.000081245, 0.000081245, 0.000081245],    [0.000065587, 0.000071169, 0.000076472, 0.000078817, 0.000081147, 0.000083491, 0.000085822, 0.000088166, 0.000090497, 0.000092841, 0.000095172, 0.000097516, 0.000099846, 0.000099846, 0.000099846, 0.000099846],    [0.000087915, 0.000093497, 0.000099079, 0.000101479, 0.000103879, 0.00010628, 0.00010868, 0.000111094, 0.000113494, 0.000115894, 0.000118295, 0.000120695, 0.000123095, 0.000123095, 0.000123095, 0.000123095],    [0.00010187, 0.000106056, 0.000110243, 0.000112755, 0.00011528, 0.000117792, 0.000120304, 0.00012283, 0.000125342, 0.000127854, 0.000130365, 0.000132891, 0.000135403, 0.000135403, 0.000135403, 0.000135403],    [0.000114429, 0.000118616, 0.000122802, 0.000124756, 0.000127937, 0.000130505, 0.000133073, 0.00013564, 0.000138208, 0.000140776, 0.000143343, 0.000145911, 0.000148479, 0.000148479, 0.000148479, 0.000148479],    [0.00013257, 0.000136059, 0.000137873, 0.000140301, 0.00014273, 0.000145158, 0.000147586, 0.000150014, 0.000150014, 0.000150014, 0.000150014, 0.000150014, 0.000150014, 0.000150014, 0.000150014, 0.000150014],    [0.000144432, 0.000146525, 0.000149596, 0.00015141, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712, 0.000153712],    [0.000152107, 0.000153503, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131, 0.000154131]])
    ################## Compressor efficiency ################################
    etaC = comp_eff_factor *    np.array([    [0,  0.269936013, 0.563037443, 0.663649957, 0.708410255, 0.735305698, 0.727256697, 0.69928151, 0.657073334, 0.600239533, 0.51582318, 0.392437883, 0.155777619, 0, 0, 0],    [0.441713475, 0.557540564, 0.678275581, 0.710864219, 0.734422271, 0.750029481, 0.759158226, 0.766618276, 0.7663238, 0.76023797, 0.746299456, 0.723035879, 0.67356397, 0.485001396, 0.17197378, 0],    [0.632337379, 0.680435069, 0.719796647, 0.736483601, 0.752483444, 0.762004824, 0.768385129, 0.771918837, 0.772213313, 0.772507789, 0.766520117, 0.753563188, 0.725097209, 0.590816312, 0.414916191, 0.219875152],    [0.711158695, 0.740115467, 0.754250298, 0.764164312, 0.770937252, 0.775550704, 0.778299143, 0.779967838, 0.779771521, 0.777710192, 0.773489374, 0.768188812, 0.750422115, 0.643232978, 0.537123586, 0.422179924],    [0.749735005, 0.766912751, 0.77849546, 0.781636534, 0.783796022, 0.7852684, 0.785759193, 0.785857351, 0.785072083, 0.783010753, 0.779280728, 0.773587533, 0.759452701, 0.695453327, 0.629687098, 0.559896369],    [0.770446459, 0.780164155, 0.786937095, 0.788409474, 0.789391059, 0.789881852, 0.789783693, 0.789391059, 0.788311315, 0.786348144, 0.783108912, 0.777710192, 0.764655105, 0.728238282, 0.68504852, 0.639601112],    [0.778200984, 0.783697863, 0.788311315, 0.789391059, 0.790274486, 0.789685535, 0.787231571, 0.78458129, 0.782716278, 0.780360473, 0.778102826, 0.775256228, 0.769759349, 0.728238282, 0.68504852, 0.639601112],    [0.779084411, 0.783305229, 0.786740778, 0.787722364, 0.788802108, 0.788900266, 0.788703949, 0.788409474, 0.788016839, 0.787722364, 0.787133412, 0.785759193, 0.783501546, 0.756900579, 0.716066622, 0.673171336],    [0.763084568, 0.763477202, 0.76494958, 0.766912751, 0.768385129, 0.769268556, 0.769955666, 0.769072239, 0.75071659, 0.735109381, 0.735109381, 0.716950049, 0.695158851, 0.672582385, 0.637539782, 0.600730326],    [0.70674156, 0.709686317, 0.711649488, 0.712631073, 0.711649488, 0.69996862, 0.689661972, 0.681612971, 0.665220493, 0.652656199, 0.639895587, 0.622423366, 0.604558509, 0.583258104, 0.557442405, 0.527307731],    [0.618398865, 0.618398865, 0.618398865, 0.611920401, 0.606717998, 0.588067873, 0.581294933, 0.567454578, 0.556755296, 0.545270745, 0.531234073, 0.516019497, 0.498841751, 0.475381858, 0.448977208, 0.448977208]])

    ################### Compressor pressure ratio ###########################
    Pivolvo = np.array([    [1.04646, 1.0758, 1.105629, 1.1244066, 1.1291988, 1.12959, 1.1220594, 1.1107146, 1.0972182, 1.0817658, 1.062597, 1.0388316, 1.0005918, 0.8802, 0.6846, 0.489],    [1.4181, 1.4670, 1.5011322, 1.5205944, 1.5306678, 1.5338952, 1.5307656, 1.526169, 1.5147264, 1.4983938, 1.4760954, 1.44744, 1.4008872, 1.2714, 1.0758, 0.8802],    [1.7593242, 1.8126252, 1.8526254, 1.8647526, 1.8747282, 1.8747282, 1.8697404, 1.860156, 1.8462684, 1.831794, 1.8096912, 1.7776128, 1.7269524, 1.5648, 1.3692, 1.1736],    [2.2922364, 2.3333124, 2.3448528, 2.3526768, 2.3517966, 2.3451462, 2.3340948, 2.321283, 2.3028966, 2.280207, 2.2527252, 2.2241676, 2.1689106, 1.956, 1.7604, 1.5648],    [2.9895504, 3.010284, 3.0098928, 3.0032424, 2.9913108, 2.9762496, 2.9576676, 2.937423, 2.9136576, 2.885589, 2.8516524, 2.811261, 2.7440724, 2.5428, 2.3472, 2.1516],    [3.9102396, 3.9089682, 3.8918532, 3.874347, 3.8540046, 3.8305326, 3.8038332, 3.7744932, 3.7419258, 3.7039794, 3.6590892, 3.6030498, 3.5091618, 3.3252, 3.0807, 2.8362],    [4.4730786, 4.4634942, 4.431318, 4.4022714, 4.3629558, 4.3372344, 4.2950826, 4.2589944, 4.216158, 4.1715612, 4.1220744, 4.0745436, 4.0111692, 3.7653, 3.5208, 3.2763],    [5.1107346, 5.093913, 5.0651598, 5.047458, 5.0126412, 4.977042, 4.9440834, 4.912494, 4.8683862, 4.8334716, 4.7943516, 4.7494614, 4.6975296, 4.4988, 4.2054, 3.912],    [5.7983664, 5.7964104, 5.7865326, 5.7729384, 5.755041, 5.7267768, 5.703207, 5.6511774, 5.4768, 5.30076, 5.15406, 4.9878, 4.7922, 4.5966, 4.3032, 4.0098],    [6.2592, 6.2592, 6.2592, 6.24942, 6.23964, 6.09294, 5.9658, 5.868, 5.6724, 5.5257, 5.379, 5.1834, 4.9878, 4.76286, 4.4988, 4.2054],    [6.47436, 6.45969, 6.44502, 6.34722, 6.26898, 6.1125, 5.99514, 5.89734, 5.70174, 5.55504, 5.39856, 5.21274, 5.01714, 4.80198, 4.51836, 4.21518]])

    beta_vec_grid, omega_vec_grid =  np.meshgrid(beta_c, nrott, copy=False)

    beta_vec_grid = beta_vec_grid.flatten()
    omega_vec_grid = omega_vec_grid.flatten()

    eta_TLU1 = etaC.flatten()
    mdot_TLU1 = cairvolvo_comp.flatten()
    pr_TLU1 = Pivolvo.flatten()
    # compressor_map_df = pd.DataFrame({'mdot_corr':mdot_TLU1,'N_corr': omega_vec_grid, 'ETA':eta_TLU1, 'Beta':beta_vec_grid, 'PR':pr_TLU1})
    compressor_map_df = pd.DataFrame({'mdot_corr':mdot_TLU1,'N_corr': omega_vec_grid, 'ETA':eta_TLU1, 'PR':pr_TLU1})
    compressor_map_df.to_pickle('ANN Model Compressor Map/compressor_map_df.pkl')
    
    return


    

    

#     return nrott, beta_c, cairvolvo_comp, etaC, Pivolvo, area_A_C, area_B_C


# In[25]:


# for ANN model with turbine map
def turbine_map(turb_area_in_factor, turb_area_out_factor, turb_m_factor, turb_eff_factor):
    area_A_T = turb_area_in_factor * 0.01
    area_B_T = turb_area_out_factor * 0.01
    return turb_m_factor, turb_eff_factor, area_A_T, area_B_T



import joblib
from keras.models import load_model
import numpy as np
import math

def diffuser_map():
    Cp_diff = 0.64479
    return Cp_diff



import joblib
from keras.models import load_model
import numpy as np
import math

def combustor_map(combust_area_in_factor, combust_area_out_factor, combust_kcc_factor, combust_Q_loss_coeff_factor):
#     k_cc = k_cc_factor * 0.0015617413667629305 # this design value is correct if pressure is in bar
    area_A_air_CC = combust_area_in_factor * 0.01
    area_A_fuel_CC = 0.001
    area_B_CC = combust_area_out_factor * 0.01    
    
    
    
    
    k_cc_des = 19982497
    k_cc = combust_kcc_factor * k_cc_des # this design value is correct if pressure is in Pa
    
    Q_loss_coeff_des = 0.015319256347879054
    eta = 0.998 # Efficiency of combustion
    Q_loss_coeff = combust_Q_loss_coeff_factor * Q_loss_coeff_des
    

  
    
    return k_cc, eta, Q_loss_coeff, area_A_air_CC, area_A_fuel_CC, area_B_CC



import joblib
from keras.models import load_model
import numpy as np
import math

# def recuperator_map(recup_cs_area_factor, recup_hs_area_factor, recup_dp_coeff_cs_factor, recup_dp_coeff_hs_factor, eta_slope_1_factor, eta_slope_2_factor, eta_opt_factor, recup_m_opt_factor, recup_Q_loss_factor):
def recuperator_map(recup_cs_area_factor, recup_hs_area_factor, recup_dp_coeff_cs_factor, recup_dp_coeff_hs_factor, recup_m_min1_coeff_factor, recup_eta_min1_coeff_factor, recup_m_min2_coeff_factor, recup_eta_min2_coeff_factor, recup_eta_opt_factor, recup_m_opt_factor, recup_Q_loss_factor):   
    
    area_A_cs_R = recup_cs_area_factor * 0.01
    area_B_cs_R = area_A_cs_R
    area_A_hs_R = recup_hs_area_factor * 0.012
    area_B_hs_R = area_A_hs_R
    
    cold_air_pressure_inlet_des = 4.3891e5
    cold_air_pressure_outlet_des = 4.2972e5
    cold_air_mass_flow_inlet_des = 0.7766
    cold_air_temperature_inlet_des = 211.9360 + 273.15
    cold_air_temperature_outlet_des = 607.4800 + 273.15

    hot_air_pressure_inlet_des = 1.0619e5
    hot_air_pressure_outlet_des = 1.0339e5
    hot_air_mass_flow_inlet_des = 0.7829
    hot_air_temperature_inlet_des = 647.0870 + 273.15
    

    dp_coeff_cs_R = recup_dp_coeff_cs_factor * (cold_air_pressure_inlet_des - cold_air_pressure_outlet_des) / cold_air_pressure_inlet_des * 1/(cold_air_mass_flow_inlet_des**2/cold_air_pressure_inlet_des**2)/((cold_air_temperature_outlet_des**1.55)/(cold_air_temperature_inlet_des**0.55))
    dp_coeff_hs_R = recup_dp_coeff_hs_factor * (hot_air_pressure_inlet_des - hot_air_pressure_outlet_des) / hot_air_pressure_inlet_des / (hot_air_mass_flow_inlet_des**2) / (hot_air_temperature_inlet_des)
#     eta_ht_R = (cold_air_temperature_outlet_des - cold_air_temperature_inlet_des) / (hot_air_temperature_inlet_des - cold_air_temperature_inlet_des)
#     eta_ht_R = recup_eff_ht_factor * eta_ht_R
    
    
#     recup_m_opt_nom = 0.63; recup_ht_coeff_nom = -2.4
    recup_m_opt_nom = 0.63; eta_opt_nom = 0.93
#     eta_slope_1_nom = 0.15; eta_slope_2_nom = -0.4;
    recup_Q_loss_nom = 0.01
    recup_m_min1_coeff_nom = 0.9
    recup_eta_min1_coeff_nom = 0.9
    recup_m_min2_coeff_nom = 1.1
    recup_eta_min2_coeff_nom = 0.9
    
#     ht_coeff_R = recup_ht_coeff_factor * recup_ht_coeff_nom
    
#     eta_slope_1_R = eta_slope_1_factor * eta_slope_1_nom
#     eta_slope_2_R = eta_slope_2_factor * eta_slope_2_nom
    
    m_min1_coeff_R = recup_m_min1_coeff_factor * recup_m_min1_coeff_nom
    eta_min1_coeff_R = recup_eta_min1_coeff_factor * recup_eta_min1_coeff_nom
    m_min2_coeff_R = recup_m_min2_coeff_factor * recup_m_min2_coeff_nom
    eta_min2_coeff_R = recup_eta_min2_coeff_factor * recup_eta_min2_coeff_nom
    
    eta_opt_R = recup_eta_opt_factor * eta_opt_nom
    m_opt_R = recup_m_opt_factor * recup_m_opt_nom
    
    Q_loss_R = recup_Q_loss_factor * recup_Q_loss_nom

    return dp_coeff_cs_R, dp_coeff_hs_R, m_min1_coeff_R, eta_min1_coeff_R, m_min2_coeff_R, eta_min2_coeff_R, m_opt_R, eta_opt_R, Q_loss_R, area_A_cs_R, area_B_cs_R, area_A_hs_R, area_B_hs_R



import joblib
from keras.models import load_model
import numpy as np
import math

def heat_exchanger_map():

    mdot_HE = np.array([0.04, 0.05, 0.09, 0.11, 0.13, 0.14, 0.15, 0.16, 0.17, 0.19, 0.2 , 0.22,                        0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3 , 0.31, 0.32, 0.33, 0.35,                        0.36, 0.37, 0.38, 0.39, 0.4 , 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47,                        0.48, 0.49, 0.5 , 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59,                        0.6 , 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.7 , 0.71,                        0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.8 , 0.81])
    dp_HE = 1e-5 * np.array([11.49, 22.7 , 31.95, 25.92, 34.65, 33.09, 27.96, 38.24, 40.04, 38.69, 40.03,                             52.14, 52.07, 55.45, 60.18, 56.15, 62.63, 59.3 , 65.52, 78.54, 77.6 , 78.89,                             84.31, 93.64, 96.57, 99.09, 106.17, 113.78, 118.88, 118.88, 118.88, 118.88,                             116.5, 135.14, 137.96, 156.61, 156.58, 158.83, 162.18, 173.73, 178.64,                             187.11, 193.68, 199.48, 209.52, 236.58, 220.04, 228.78, 243, 245.27, 272.49,                             275.96, 288.37, 294.38, 304.96, 316.23, 330.68, 337.52, 350.36, 354.62,                             378.94, 383.02, 402.03, 401.57, 421.43, 430.46, 439.94, 465.33, 468.01, 480.67])
    return mdot_HE, dp_HE
    
    



import joblib
from keras.models import load_model
import numpy as np
import math

# def shaft_loss_map(Uloss_factor, eta_mech_factor):
    
#     Uloss_des = .08; #hipshot/designpower;
#     eta_mech_des = 0.9910832874831639
    
#     shaft_loss_coeff = Uloss_factor * Uloss_des
#     shaft_mech_eff = eta_mech_factor * eta_mech_des
    
#     return shaft_loss_coeff, shaft_mech_eff



import joblib
from keras.models import load_model
import numpy as np
import math

def shaft_loss_map(W_loss_a_factor, W_loss_b_factor, W_loss_c_factor):
    
    W_loss_a_des = -2e-7
    W_loss_b_des = 0.0316
    W_loss_c_des = -120.57
    
    W_loss_a = W_loss_a_des * W_loss_a_factor
    W_loss_b = W_loss_b_des * W_loss_b_factor
    W_loss_c = W_loss_c_des * W_loss_c_factor
    
    
    
    
    # DLR Correlation for Loss
    
#     W_loss_val= 3473 + 0.0812 * W_turbo_val + 2.67 * 1e-7*W_turbo_val**2 -4.48e-12*W_turbo_val**3

    W_loss_d_des = -4.48e-12
    W_loss_a_des = 2.67 * 1e-7
    W_loss_b_des = 0.0812
    W_loss_c_des = 3473
    
    W_loss_a = W_loss_a_des * W_loss_a_factor
    W_loss_b = W_loss_b_des * W_loss_b_factor
    W_loss_c = W_loss_c_des * W_loss_c_factor    
    
    
    return W_loss_a, W_loss_b, W_loss_c
