#!/usr/bin/env python
# coding: utf-8


import numpy as np
import math

# In[ ]:


def nn_function(nn, X, scaler=None):
    
    try:
        X_array = X.to_numpy()
    except:
        try:
            X_array = np.array(X)
        except:
            X_array = X
    try:
        rows, cols = X_array.shape
        
    except:
        rows = 1
        cols = len(X_array)
        

    if scaler is not None:
        X_norm = transformer(X_array, scaler, side=0)
    else:
        X_norm = X_array
        
    
    if X_norm.ndim == 1:
        X_norm = np.array([X_norm])
    
    
#     y_norm = nn.predict(X_norm)
    y_norm = nn(X_norm)
    
    if y_norm.shape == (1,len(y_norm[0])) and y_norm.ndim == 2:
        y_norm = y_norm[0]
    
    
    if scaler is not None:
        y = detransformer(y_norm, scaler, side=1)
    else:
        y = y_norm  
        
    return y
        



# In[ ]:


def transformer(data, scaler, side=-1):
    scaler_max = scaler.data_max_
    scaler_min = scaler.data_min_
    scaler_lenght = len(scaler_max)
 
    # if side = -1 it meanes that the data shape is fit to the scaler
    # if side = 0 it meanes that the data shape is not fit and from the left side we should use the scaler
    # if side = 1 it meanes that the data shape is not fit and from the right side we should use the scaler
    
    try:
        data_array = data.to_numpy()
    except:
        try:
            data_array = np.array(data)
        except:
            pass
    try:
        rows, cols = data_array.shape
        
    except:
        rows = 1
        cols = len(data_array)
    
    if cols < scaler_lenght:
        if side == 0:
            scaler_max = scaler_max[0:cols]
            scaler_min = scaler_min[0:cols]
        elif side == 1:
            scaler_max = scaler_max[-cols:]
            scaler_min = scaler_min[-cols:]  
            
        else:
            pass
    
    
    if rows > 1:
        normalized_data = np.empty([rows, cols])
        
        for row_no in range(rows):
            for col_no in range(cols):
                normalized_data[row_no,col_no] =(data_array[row_no,col_no] - scaler_min[col_no])/(scaler_max[col_no]-scaler_min[col_no])
    else:
        normalized_data = np.empty([cols,])
        for col_no in range(cols):
            normalized_data[col_no] =(data_array[col_no] - scaler_min[col_no])/(scaler_max[col_no]-scaler_min[col_no])
    return normalized_data
   


# In[ ]:


def detransformer(normal_data, scaler, side=-1):
    scaler_max = scaler.data_max_
    scaler_min = scaler.data_min_
    scaler_lenght = len(scaler_max)
 
    # if side = -1 it meanes that the data shape is fit to the scaler
    # if side = 0 it meanes that the data shape is not fit and from the left side we should use the scaler
    # if side = 1 it meanes that the data shape is not fit and from the right side we should use the scaler
    
    try:
        normal_data_array = normal_data.to_numpy()
    except:
        try:
            normal_data_array = np.array(normal_data)
        except:
            pass
    try:
        rows, cols = normal_data_array.shape
        
    except:
        rows = 1
        cols = len(normal_data_array)
    
    if cols < scaler_lenght:
        if side == 0:
            scaler_max = scaler_max[0:cols]
            scaler_min = scaler_min[0:cols]
        elif side == 1:
            scaler_max = scaler_max[-cols:]
            scaler_min = scaler_min[-cols:]  
            
        else:
            pass
    
    
    if rows > 1:
        actual_data = np.empty([rows, cols])
        
        for row_no in range(rows):
            for col_no in range(cols):
                actual_data[row_no,col_no] =(normal_data_array[row_no,col_no])*(scaler_max[col_no]-scaler_min[col_no]) + scaler_min[col_no]
    else:
        actual_data = np.empty([cols,])
        for col_no in range(cols):
            actual_data[col_no] =(normal_data_array[col_no])*(scaler_max[col_no]-scaler_min[col_no]) + scaler_min[col_no]
    return actual_data
        
    
    
    
    
    


# In[ ]:


def component_intake(intake_data, mdot_in, p_in, T_in, x_f_in):
    dp_coeff_intake, dT_coeff_intake, dT_intercept_intake = intake_decomposer(intake_data)
    dp = dp_coeff_intake * mdot_in * math.sqrt(T_in)/p_in
    dT = dT_coeff_intake * (T_in-273.15) + dT_intercept_intake
#     print('dT_coeff_intake:',dT_coeff_intake)
#     print('dT_intercept_intake:',dT_intercept_intake)
#     print('dT:',dT)
    T_out = T_in + dT
    mdot_out = mdot_in
    x_f_out = x_f_in
    p_out = p_in - dp
    return mdot_out, p_out, T_out, x_f_out


# In[ ]:


def component_compressor(compressor_data, mdot_in, p_in, T_in, x_f_in, N):
    
    pr, eta, area_in, area_out, eta_mech = compressor_decomposer(compressor_data, mdot_in, p_in, T_in, N)
    ps_in, Ts_in, M_in, cp_in, cv_in, gamma_in, R_in, wfr_gas = flow_properties_calculator(p_in, T_in, mdot_in, x_f_in, area_in)
    
    mdot_out = mdot_in
    x_f_out = x_f_in
    p_out = p_in * pr
    
    p_out_isen, T_out_isen = isentropic_process(Ts_in, ps_in, p_out, mdot_out, R_in, area_out, wfr_gas )    
    ps_out_isen, Ts_out_isen, M_out_isen, cp_out_isen, cv_out_isen, gamma_out_isen, R_out_isen, wfr_gas = flow_properties_calculator(p_out_isen, T_out_isen, mdot_out, x_f_out, area_out)
    h_in = enthalpy_calculator(Ts_in, ps_in, wfr_gas, T_in)
    delta_h_isen = enthalpy_calculator(Ts_out_isen, ps_out_isen, wfr_gas, T_out_isen) - h_in
    delta_h = delta_h_isen / eta
    h_out = h_in + delta_h 
    T_out = T_based_on_enthalpy(h_out, p_out, mdot_out, wfr_gas, area_out)
    W = 1/eta_mech * mdot_out * (h_out - h_in)
    return mdot_out, p_out, T_out, x_f_out, -W, eta


# In[ ]:


def component_turbine(turbine_data, mdot_in, p_in, T_in, x_f_in, N):
#     print('>>>>>>>>>TURBINE')
    pr, eta, area_in, area_out, eta_mech = turbine_decomposer(turbine_data, mdot_in, p_in, T_in, N)
    ps_in, Ts_in, M_in, cp_in, cv_in, gamma_in, R_in, wfr_gas = flow_properties_calculator(p_in, T_in, mdot_in, x_f_in, area_in)
    
    
    mdot_out = mdot_in
    x_f_out = x_f_in
    ps_out = p_in / pr
    
    ps_out_isen = ps_out # assumption
    Ts_out_isen = isentropic_process_temperature_calculator(Ts_in, ps_in, ps_out_isen, R_in, wfr_gas)

    
    R_out = R_in;
    p_out_isen, T_out_isen, M_out_isen = stagnation_properties_calculator(Ts_out_isen, ps_out, mdot_out, area_out, R_out, wfr_gas)
    h_in = enthalpy_calculator(Ts_in, ps_in, wfr_gas, T_in)
    
    delta_h_isen = enthalpy_calculator(Ts_out_isen, ps_out_isen, wfr_gas, T_out_isen) - h_in
    
    
    delta_h = delta_h_isen * eta
    h_out = h_in + delta_h 
    T_out = T_based_on_enthalpy(h_out, p_out_isen, mdot_out, wfr_gas, area_out)
    
    
    p_out, M_out = flow_properties_based_on_T_ps(T_out, ps_out, mdot_out, area_out, R_out, wfr_gas)
    W = eta_mech * mdot_out * (h_out - h_in)
    return mdot_out, p_out, T_out, x_f_out, -W, eta, ps_out


# In[ ]:


def component_diffuser(diffuser_data, mdot_in, p_in, T_in, x_f_in, ps_in):
#     print('>>>>>>>>>DIFFUSER')
    Cp_diff = diffuser_decomposer(diffuser_data)
    ps_out = (p_in - ps_in) * Cp_diff + ps_in
    p_out = ps_out
    mdot_out = mdot_in
    x_f_out = x_f_in
    T_out = T_in
    return mdot_out, p_out, T_out, x_f_out


# In[ ]:


def component_recuperator_cs(recuperator_data, mdot_in_cs, p_in_cs, T_in_cs, x_f_in_cs, T_in_hs):
    
    dp_coeff_cs, dp_coeff_hs, m_min1_coeff, eta_min1_coeff, m_min2_coeff, eta_min2_coeff, m_opt, eta_opt, Q_loss, area_in_cs, area_out_cs, area_in_hs, area_out_hs = recuperator_decomposer(recuperator_data)
    
    m_min1 = m_min1_coeff * m_opt
    m_min2 = m_min2_coeff * m_opt
    eta_min1 = eta_min1_coeff * eta_opt
    eta_min2 = eta_min2_coeff * eta_opt
    
    
    
    mdot_out_cs = mdot_in_cs
    x_f_out_cs = x_f_in_cs
    
        
    if abs(mdot_in_cs-m_opt)/abs(m_opt) < 0.005:
        eff_ht = eta_opt
    elif mdot_in_cs < m_opt:
        eff_ht = (eta_opt - eta_min1)/(m_opt - m_min1)**2 * (mdot_in_cs - m_min1)**2 + eta_min1 
    else:
        eff_ht = (eta_opt - eta_min2)/(m_opt - m_min2)**2 * (mdot_in_cs - m_min2)**2 + eta_min2 
    T_out_cs = T_in_cs + eff_ht * (T_in_hs - T_in_cs)
    p_out_cs = p_in_cs - p_in_cs * ((mdot_in_cs / p_in_cs)**2) * ((T_out_cs**1.55) / (T_in_cs**0.55)) * dp_coeff_cs
    ps_in_cs, Ts_in_cs, M_in_cs, cp_in_cs, cv_in_cs, gamma_in_cs, R_in_cs, wfr_gas_cs = flow_properties_calculator(p_in_cs, T_in_cs, mdot_in_cs, x_f_in_cs, area_in_cs)
    ps_out_cs, Ts_out_cs, M_out_cs, cp_out_cs, cv_out_cs, gamma_out_cs, cp_coeff_out_cs, wfr_gas_cs = flow_properties_calculator(p_out_cs, T_out_cs, mdot_out_cs, x_f_out_cs, area_out_cs)
    h_in_cs = enthalpy_calculator(Ts_in_cs, ps_in_cs, wfr_gas_cs, T_in_cs)
    h_out_cs = enthalpy_calculator(Ts_out_cs, ps_out_cs, wfr_gas_cs, T_out_cs)
    Q_cs = mdot_in_cs * (h_out_cs - h_in_cs)
    
    return mdot_out_cs, p_out_cs, T_out_cs, x_f_out_cs, Q_cs, eff_ht


# In[ ]:


def component_recuperator_hs(recuperator_data, mdot_in_hs, p_in_hs, T_in_hs, x_f_in_hs, Q_cs):
#     print('>>>>>>>>>RECUPERATOR HS')
    dp_coeff_cs, dp_coeff_hs, m_min1_coeff, eta_min1_coeff, m_min2_coeff, eta_min2_coeff, m_opt, eta_opt, Q_loss, area_in_cs, area_out_cs, area_in_hs, area_out_hs = recuperator_decomposer(recuperator_data)

    mdot_out_hs = mdot_in_hs
    x_f_out_hs = x_f_in_hs
    p_out_hs = p_in_hs - p_in_hs * (mdot_in_hs**2) * T_in_hs * dp_coeff_hs
        

    ps_in_hs, Ts_in_hs, M_in_hs, cp_in_hs, cv_in_hs, gamma_in_hs, R_in_hs, wfr_gas_hs = flow_properties_calculator(p_in_hs, T_in_hs, mdot_in_hs, x_f_in_hs, area_in_hs)
    h_in_hs = enthalpy_calculator(Ts_in_hs, ps_in_hs, wfr_gas_hs, T_in_hs)
    
    Q_hs = - Q_cs
    
    Q_hs = -(Q_cs * (1 + Q_loss))
    
    h_out_hs = h_in_hs + Q_hs / mdot_in_hs
    T_out_hs = T_based_on_enthalpy(h_out_hs, p_out_hs, mdot_out_hs, wfr_gas_hs, area_out_hs)

    return mdot_out_hs, p_out_hs, T_out_hs, x_f_out_hs, Q_hs


# In[ ]:


def component_combustor(combustor_data, mdot_in_air, p_in_air, T_in_air, x_f_in_air,                       mdot_in_fuel, p_in_fuel, T_in_fuel, x_f_in_fuel):
    k_cc, eta, Q_loss_coeff, area_in_air, area_in_fuel, area_out = combustor_decomposer(combustor_data)
    
    mdot_fuel_in = mdot_in_air * x_f_in_air + mdot_in_fuel * x_f_in_fuel
    mdot_fuel_out = mdot_fuel_in
    mdot_in = mdot_in_air + mdot_in_fuel
    mdot_out = mdot_in
    mdot_out_fuel = mdot_in_fuel  
    mdot_air_out = mdot_out - mdot_out_fuel
    x_f_out = mdot_out_fuel / mdot_out

    wfr_gas_out = weight_fraction_calculator(air_fuel_composition, mdot_air_out, mdot_out_fuel)
    
    ps_in_air, Ts_in_air, M_in_air, cp_in_air, cv_in_air, gamma_in_air, R_in_air, wfr_gas_air = flow_properties_calculator(p_in_air, T_in_air, mdot_in_air, x_f_in_air, area_in_air)
    h_in_air = enthalpy_calculator(Ts_in_air, ps_in_air, wfr_gas_air, T_in_air)

    fuel_wfr, LHV, m_fuel_nom, M_fuel = fuel_composition_calculator(methane_percentage, hydrogen_percentage)

    H_fuel = mdot_fuel_in * LHV * 1000
    Q = eta * H_fuel
    H_air = mdot_in_air * h_in_air
    
    H_out = (H_fuel + H_air) * (1 - Q_loss_coeff)
    
    h_out = H_out / mdot_out
    T_out = T_in_air # first guess
    error = 2
    while error > 1:
        T_out_reserve = T_out
        dp = p_in_air * k_cc * ((mdot_in * math.sqrt(T_in_air) / (p_in_air))**2) * (1 + 0.2 * (T_out/T_in_air -1)) 
        p_out = p_in_air - dp
        T_out = T_based_on_enthalpy(h_out, p_out, mdot_out, wfr_gas_out, area_out)
        error = abs(T_out_reserve - T_out)
    
    return mdot_out, p_out, T_out, x_f_out, Q , eta


# In[ ]:


def component_heat_exchanger(heat_exchanger_data, mdot_in, p_in, T_in, x_f_in):
#     print('>>>>>>>>>HE')

    mdot_HE, dp_HE = heat_exchanger_decomposer(heat_exchanger_data)
    
    dp = interpolator1d(mdot_HE, dp_HE, mdot_in)
    p_out = p_in - dp
    mdot_out = mdot_in
    x_f_out = x_f_in
    T_out = T_in
    return mdot_out, p_out, T_out, x_f_out


# In[9]:

if False:
    air_fuel_composition_methane = [74.86597681087144, 0,  0,  25.134023189128534,  0,  0,  0,  23.132998547685872, 75.55299525670301, 1.2629999207075284, 0.0, 0.04999999686094729, 6.278105410508923e-06, 0.0]
    air_fuel_composition_des = air_fuel_composition_methane
    x_f_air = 0
    wfr_gas_31_des = weight_fraction_calculator(air_fuel_composition_des, m3_des, x_f_air)
    h_in_air = enthalpy_calculator(t031_des+273.15, p031_des * 100000, wfr_gas_31_des, t031_des+273.15)

    H_air_des = m31_des * h_in_air

    LHV_fuel_des = 48.2*10**6
    x_f_des = 0.009086
    mf_des = x_f_des * m31_des
    H_f_des = mf_des * LHV_fuel_des

    wfr_gas_32_des = weight_fraction_calculator(air_fuel_composition_des, m32_des, x_f_des)
    h_out = enthalpy_calculator(t032_des+273.15, p032_des * 100000, wfr_gas_32_des, t032_des+273.15)


    Q_loss_design =  (H_air_des + H_f_des) - m32_des * h_out
    Q_loss_coeff = Q_loss_design / H_f_des


    # In[10]:


    ############# mechanical loss #################
    oiltemp_in = 40;
    oiltemp_ut = 60;
    density_oil = 775; #[kg/m3]
    volumef_oil = 3.3333e-005; #[m3/s]
    massf_oil = density_oil * volumef_oil; #[kg/s]
    Cp_oil = 2090; #[j/KgK]
    mechanical_loss = Cp_oil * (oiltemp_ut - oiltemp_in) * massf_oil;
    designpower = (274352.91 - 153251.94);
    eta_mech = 1 - mechanical_loss / designpower;
    ############# unknown losses #################
    hipshot = 10000; #[W]
    Uloss = .08; #hipshot/designpower;

