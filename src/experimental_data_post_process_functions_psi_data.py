#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Python ≥3.5 is required
import sys
assert sys.version_info >= (3, 5)

import datetime
import time
import math
from scipy.signal import lfilter


import numpy as np
import matplotlib.pyplot as plt
from tsmoothie.smoother import *


# Scikit-Learn ≥0.20 is required
import sklearn
assert sklearn.__version__ >= "0.20"

# Common imports
import numpy as np
import pandas as pd
import os
import glob

# To plot pretty figures
import matplotlib as mpl
import matplotlib.pyplot as plt
# from terminaltables import AsciiTable

import warnings
warnings.filterwarnings('ignore')

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 1000)


# In[ ]:


##########
def variable_name_modifier_PSI(data_frame, reserved_units, excel_file_path, atmospheric_pressure=None, excel_sheet_name=None, label_with_tag = True, original_sensor_name = None, print_msg=None):    
    if print_msg is None:
        print_msg = False
    
    
    if atmospheric_pressure is None:
        atmospheric_pressure = 1.01325
    
    if original_sensor_name is None:
        original_sensor_name = True # meaning that the dataframe has sensors with the original naming
    else:
        pass
    if excel_sheet_name is None:
        excel_sheet_name = 'Sensors Description'
    
    unf_var_names = []
    variable_description = list()

    sensor_name_reference = pd.Series(dtype = object)
    xls = pd.ExcelFile(excel_file_path)
    sensor_data = pd.read_excel(xls, excel_sheet_name)
    sensor_unit_modifier_data = pd.read_excel(xls, 'Unit Modifier')
    if original_sensor_name:
        sensor_name_reference = sensor_data['Name']
        sensor_unit_reference = sensor_unit_modifier_data['Old Unit']
    else:
        sensor_name_reference_wo_unit = sensor_data['Tag']
        for number in range(len(sensor_name_reference_wo_unit)):
            sensor_name_reference = sensor_name_reference.append(pd.Series(sensor_name_reference_wo_unit[number] + ' [' + sensor_data['Unit'].iloc[number] + ']'), ignore_index = True)

    # Adding units to column names
    col_no = 0
    for col_name in data_frame.columns:
        matches = sensor_name_reference[sensor_name_reference.eq(col_name)]
        possible_index = matches.index
        flag_found_sensor_name = False
        
        for index in possible_index:

            if sensor_name_reference[index] == col_name and reserved_units[col_no] == '[' + sensor_unit_reference[index] + ']':

                correct_index = index
                tag = sensor_data['Tag'][correct_index]
                unit = sensor_data['Unit'][correct_index]
                des = sensor_data['Description'][correct_index]
                unit = ' [' + unit +']'

                flag_found_sensor_name = True
                break
        
        
        if original_sensor_name: #meaning that this is the first time df is being loaded
            matches_unit_modifier = sensor_unit_modifier_data[sensor_unit_modifier_data.eq(col_name)]
            possible_index_unit_modifier = matches_unit_modifier.index
            for index_unit_modifier in possible_index_unit_modifier:
                
                if sensor_name_reference[index_unit_modifier] == col_name:
                    correct_unit_index = index_unit_modifier
                    unit_modifier_coef = sensor_unit_modifier_data['Multipy by'].iloc[correct_unit_index]
                    
                    gauge_indicator = sensor_unit_modifier_data['Gauge'].iloc[correct_unit_index]
                    if type(data_frame[col_name].iloc[0]) != str:
                        if unit_modifier_coef != 1:
                            unit_modifier_coef = float(eval(unit_modifier_coef))
                            data_frame[col_name] = data_frame[col_name] * unit_modifier_coef
                    if gauge_indicator == 'yes' or gauge_indicator == 'Yes' or gauge_indicator == 'YES':
                        try:
                            atmospheric_pressure = data_frame['Air inlet pressure [bar]']
                        except:
                            try:
                                atmospheric_pressure = data_frame['p1 [bar]']
                            except:
                                pass
                        data_frame[col_name] = data_frame[col_name] + atmospheric_pressure 
                        
                        
                    break                                                                                           
                                                                                           
        if sensor_name_reference[index] != col_name:
            tag = col_name
            unit = ''
            des = col_name
            flag_found_sensor_name = False

        if flag_found_sensor_name is False:
            unf_var_names.append(col_name) if col_name not in unf_var_names else unf_var_names
            
        col_name_temp = col_name

        if label_with_tag is True:
            data_frame = data_frame.rename(columns={col_name_temp : tag})
            col_name_temp = tag                    
        variable_description.append([tag, unit, des]) 

            
        
        data_frame = data_frame.rename(columns={col_name_temp : (col_name_temp + unit)}) 
        col_no += 1
    print_msg = True    
    if len(unf_var_names) > 0:
        if print_msg:
            print('List of variables that were not in the excel file:')
            print(*unf_var_names, sep = ", ") 
    return data_frame, variable_description


# In[2]:


##########
def variable_name_modifier(data_frame, excel_file_path, atmospheric_pressure=None, excel_sheet_name=None, label_with_tag = True, original_sensor_name = None, print_msg=None):    
    if print_msg is None:
        print_msg = False
    
    
    if atmospheric_pressure is None:
        atmospheric_pressure = 1.01325
    
    if original_sensor_name is None:
        original_sensor_name = True # meaning that the dataframe has sensors with the original naming
    else:
        pass
    if excel_sheet_name is None:
        excel_sheet_name = 'Sensors Description'
    
    unf_var_names = []
    variable_description = list()
#     sensor_name_reference = list()
#     sensor_name_reference = pd.Series(dtype = str)
    sensor_name_reference = pd.Series(dtype = object)
    xls = pd.ExcelFile(excel_file_path)
    sensor_data = pd.read_excel(xls, excel_sheet_name)
    sensor_unit_modifier_data = pd.read_excel(xls, 'Unit Modifier')
    if original_sensor_name:
        sensor_name_reference = sensor_data['Name']
        sensor_unit_reference = sensor_unit_modifier_data['Name']
    else:
        sensor_name_reference_wo_unit = sensor_data['Tag']
        for number in range(len(sensor_name_reference_wo_unit)):
            sensor_name_reference = sensor_name_reference.append(pd.Series(sensor_name_reference_wo_unit[number] + ' [' + sensor_data['Unit'].iloc[number] + ']'), ignore_index = True)

    # Adding units to column names
    for col_name in data_frame.columns:
        print('col_name=', col_name)
        
#         matches = sensor_name_reference[sensor_name_reference.str.match(col_name)]
    
        matches = sensor_name_reference[sensor_name_reference.eq(col_name)]
        possible_index = matches.index
        flag_found_sensor_name = False
        for index in possible_index:
#             if sensor_data['Name'][index] == col_name:    
    
            if sensor_name_reference[index] == col_name:
                correct_index = index
                tag = sensor_data['Tag'][correct_index]
                unit = sensor_data['Unit'][correct_index]
                des = sensor_data['Description'][correct_index]
                unit = ' [' + unit +']'

                flag_found_sensor_name = True
                break
        if original_sensor_name: #meaning that this is the first time df is being loaded
            matches_unit_modifier = sensor_unit_modifier_data[sensor_unit_modifier_data.eq(col_name)]
            possible_index_unit_modifier = matches_unit_modifier.index
            for index_unit_modifier in possible_index_unit_modifier:
                if sensor_unit_reference[index_unit_modifier] == col_name:
                    correct_unit_index = index_unit_modifier
                    unit_modifier_coef = sensor_unit_modifier_data['Multipy by'].iloc[correct_unit_index]
                    gauge_indicator = sensor_unit_modifier_data['Gauge'].iloc[correct_unit_index]
                    if type(data_frame[col_name].iloc[0]) != str:
                        if unit_modifier_coef != 1:
                            unit_modifier_coef = float(eval(unit_modifier_coef))
                            data_frame[col_name] = data_frame[col_name] * unit_modifier_coef
                    if gauge_indicator == 'yes' or gauge_indicator == 'Yes' or gauge_indicator == 'YES':
                        try:
                            atmospheric_pressure = data_frame['Air inlet pressure [bar]']
                        except:
                            try:
                                atmospheric_pressure = data_frame['p1 [bar]']
                            except:
                                pass
                        data_frame[col_name] = data_frame[col_name] + atmospheric_pressure 
                        
                        
                    break                                                                                           
                                                                                           
                                                                                           
                                                                                           
        if sensor_name_reference[index] != col_name:
            tag = col_name
            unit = ''
            des = col_name
            flag_found_sensor_name = False

        if flag_found_sensor_name is False:
            unf_var_names.append(col_name) if col_name not in unf_var_names else unf_var_names
            
        col_name_temp = col_name
        if label_with_tag is True:
            data_frame = data_frame.rename(columns={col_name_temp : tag})
            col_name_temp = tag            
#         data_frame = data_frame.rename(columns={col_name_temp : (col_name_temp + ' [' + unit +']')})
        
        variable_description.append([tag, unit, des]) 

            
        
        data_frame = data_frame.rename(columns={col_name_temp : (col_name_temp + unit)}) 
    if len(unf_var_names) > 0:
        if print_msg:
            print('List of variables that were not in the excel file:')
            print(*unf_var_names, sep = ", ") 
    return data_frame, variable_description


# In[2]:


def sensors_name_reorder(df, excel_file_path_for_sensors):
    df_temp = df.copy()

    desired_order = sensor_unit_adder(excel_file_path_for_sensors, 'Selected Sensors', 'Name', 'Tag', 'Unit')
    list1 = ['record_date [-]', 'record_time [-]', 't [sec]']
    list1.extend(desired_order)
    desired_order = list1
    complete_column_name = df.columns.values.tolist()
    complete_column_name_set = set(complete_column_name)
    common_names_ordered = [x for x in desired_order if x in complete_column_name_set]
    remaining = [x for x in complete_column_name if not x in desired_order or desired_order.remove(x)]
    common_names_ordered=common_names_ordered+remaining
    unique_common_names_ordered = []
    unique = [x for x in common_names_ordered if x not in unique_common_names_ordered and unique_common_names_ordered.append(x)]
    main_list = list(set(complete_column_name) - set(unique_common_names_ordered))

    df_temp1 = df_temp.reindex(columns=unique_common_names_ordered)
    return df_temp1
    


# In[ ]:


def pipeline_PSI_MGT_data(data_file, sensor_file, st_st_gauge_dict = {'N_act_rel [%]':[0.3,1]}):

    # Load data
    excel_data = pd.read_excel(data_file, header=4)
    
    if excel_data.iloc[0].isnull().all(): # Meaning that the first row is empty, hence, the units are included in the column names
        excel_data.drop(labels=0, axis=0, inplace=True)
    else:
        column_names = excel_data.columns
        modified_columns = list()
        for col_name in column_names:
            unit = excel_data[col_name].iloc[0]
            
            if type(excel_data[col_name].iloc[0]) == str :
#                 if not math.isnan(excel_data[col_name].iloc[0]):
                if col_name[-1] == ' ':
                    col_name = col_name[0:-1]
                if unit[0] == ' ':
                    unit = unit[1:]
            
                col_name = col_name + ' ' + unit
            modified_columns.append(col_name)
        excel_data = excel_data.set_axis(modified_columns, axis=1, inplace=False)
        excel_data.drop(labels=0, axis=0, inplace=True)
    excel_data.reset_index(drop=True, inplace=True)
    
    
    # Modify column names (some column names begin with a space character)
    col_names = excel_data.columns
    modified_col_names = list()
    
    for col_name in col_names:
        while col_name[0] == ' ':
            col_name = col_name[1:]
        modified_col_names.append(col_name)
    excel_data = excel_data.set_axis(modified_col_names, axis=1, inplace=False)
    # Modify date/time column
    excel_data = modify_date_time_col(excel_data, 'dates/times')

    # Modify some columns
    N_nom = 70000
    
    try:
        if 'speed turbine [%]' in excel_data.columns:
            
            excel_data = excel_data.rename(columns={'speed turbine [%]': 'Turbine speed [%]_temp'})
            excel_data = excel_data.rename(columns={'Turbine speed [%]': 'Turbine speed [%].1'}) 
            excel_data = excel_data.rename(columns={'Turbine speed [%]_temp': 'Turbine speed [%]'})
            excel_data = excel_data.rename(columns={'AFE performance [kW]': 'AFE power [kW]'})
    except:
        pass
    
    excel_data.insert(5, 'Turbine speed [rpm]', N_nom/100 * excel_data['Turbine speed [%]'])
    excel_data = excel_data.rename(columns={'Humidity air inlet compressor wheel MGT [∞C]': 'Humidity air inlet compressor wheel MGT [%]'})
        
    excel_data.drop(labels='Turbine speed [%].1', axis=1, inplace=True)
    excel_data['Turbine speed relative [%]'] = excel_data['Turbine speed [%]']
    
    excel_data.drop(labels='Turbine speed [%]', axis=1, inplace=True)
    
#     display(excel_data)
    
    try:
        excel_data.insert(5, 'Air inlet pressure [bar]',1/1000 * excel_data['Pressure air inlet compressor wheel MGT [mbar]'] + 1/100000 * excel_data['Air filter pressure drop [Pa]'])
    except:
        try:
            excel_data.insert(5, 'Air inlet pressure [bar]',1/1000 * excel_data['Pressure air inlet compressor wheel MGT [mbar]'] + 1/100000 * excel_data['Air filter pressure drop [pa]'])
        except:
            excel_data.insert(5, 'Air inlet pressure [bar]',1/1000 * excel_data['Pressure air inlet compressor wheel MGT [mbara]'] + 1/100000 * excel_data['Air filter pressure drop [Pa]'])

            
    try:
        excel_data = excel_data.rename(columns={'pressure gas supply natural gas [bar]': 'Pressure gas supply natural gas [bar]'})
    except:
        pass
    
    try:
        excel_data = excel_data.rename(columns={'mechanical vibration [g]': 'Mechanical vibration [g]'})
    except:
        pass

    df_columns = excel_data.columns.to_list()
    df_columns_modified = []
    units_reserve = []
    for col_name in df_columns:
    #     new_col_name = col_name.replace("∞C", "degC")
        col_name_split = col_name.split('[')
        if len(col_name_split) > 1: # meaning that the name does have the unit
            col_unit = '[' + col_name_split[1]
            col_name_split = col_name_split[0]
            if col_name_split[-1] == ' ':
                col_name_split = col_name_split[0:-1]
            new_col_name = col_name_split
            
        else:
            new_col_name = col_name
            col_unit = '[-]'

        df_columns_modified.append(new_col_name)
        
        if col_unit == '[]':
            col_unit = '[-]'
        if col_unit == '[∞C]':
            col_unit = '[degC]'
        if col_unit == '[% open]' or col_unit == '[% opened]':
            col_unit = '[%]'     
        if col_unit == '[Vdc]':
            col_unit = '[VDC]'                
        if col_unit == '[Mr]':
            col_unit = '[hr]'
        if col_unit == '[%RH]':
            col_unit = '[%]'
        if col_unit == '[G]':
            col_unit = '[g]'
                        
        if col_unit == '[pa]':
            col_unit = '[Pa]'  
        if col_unit == '[mbara]':
            col_unit = '[mbar]'              
            
            
        if col_unit == '[vol% O2]' or col_unit == '[% by volume O2]' :
            col_unit = '[%volume O2]'            
            
            
        units_reserve.append(col_unit)

    excel_data.columns = df_columns_modified
    

    excel_data, variable_description =  variable_name_modifier_PSI(excel_data, units_reserve, sensor_file, atmospheric_pressure=None, excel_sheet_name=None, label_with_tag = True, original_sensor_name = True, print_msg=None)    
    
#     # add a P_ref column:
    try:
        excel_data['P_ref [kW]'] = excel_data['P_target [kW]'] * excel_data['MGT_start_stop [-]']
    except:
        excel_data['P_ref [kW]'] = np.tile(0,len(excel_data))# for the data that does not contain 'P_target [kW]' data
    
    excel_data = sensors_name_reorder(excel_data, sensor_file)
    
    
    
    for pars in excel_data.columns:
        try:  
            excel_data[pars] = excel_data[pars].astype(float, errors = 'raise')
        except:
            pass    
    

    steady_state_rows, steady_state_time_spans = find_st_st_time_spans(excel_data, st_st_gauge_dict,time_col = 't [sec]')

    # Extracting the steady state time spans and saving the dataframe to the Excel file
    excel_data_steady_state = df_time_span_selector(excel_data, steady_state_time_spans)
    
    # excel_data_steady_state_reset_time_filtered = df_noise_cancelation(excel_data_steady_state_reset_time, method='convolution')
    excel_data_steady_state_filtered = df_noise_cancelation_for_time_spans(excel_data, steady_state_time_spans, method='convolution')
   
    # Defining df in which average values of data is availabel:
    df_col_names = excel_data_steady_state.columns
    df_col_names = df_col_names.tolist()
    time_heading = ['record_date_start [-]', 'record_date_end [-]', 'record_time_start [-]', 'record_time_end [-]', 't_start [sec]', 't_end [sec]']

    df_avg_cols = time_heading + df_col_names
    df_avg = pd.DataFrame([], columns=df_avg_cols)
    
    
    if steady_state_rows != []:
    
        average_data = []

        
        
        for st_st_row_span in steady_state_rows:
            mean_values = []
            strt_row = st_st_row_span[0]
            end_row = st_st_row_span[1]
            
            strt_date = excel_data['record_date [-]'].iloc[strt_row]
            end_date = excel_data['record_date [-]'].iloc[end_row]
            
            strt_time = excel_data['record_time [-]'].iloc[strt_row]
            end_time = excel_data['record_time [-]'].iloc[end_row]
            
            strt_t = excel_data['t [sec]'].iloc[strt_row]
            end_t = excel_data['t [sec]'].iloc[end_row]
            
            time_list = [strt_date, end_date, strt_time, end_time, strt_t, end_t, strt_date, strt_time, strt_t]
            
            for col in excel_data.columns:
                if col !='record_date [-]' and col !='record_time [-]' and col != 't [sec]':
                
                
                    try:
                        mean_value = excel_data[col].iloc[strt_row:end_row].mean()
                    except:
                        mean_value = 0
    #                 mean_values = np.append(mean_values, mean_value)
                    mean_values.append(mean_value)
            
            
            complete_list = time_list+mean_values
            average_data.append(complete_list)
            del complete_list
        
        df_avg = pd.DataFrame(average_data, columns=df_avg_cols)
        
    return excel_data, excel_data_steady_state, excel_data_steady_state_filtered, df_avg, steady_state_time_spans


# In[ ]:


def pipeline_PSI_MGT_data_2(df, st_st_gauge_dict = {'N_act_rel [%]':[0.3,1]}):
    
    excel_data = df.copy()
    excel_data.reset_index(drop=True, inplace=True)
    
       
    steady_state_rows, steady_state_time_spans = find_st_st_time_spans(excel_data, st_st_gauge_dict,time_col = 't [sec]')

    # Extracting the steady state time spans and saving the dataframe to the Excel file
    excel_data_steady_state = df_time_span_selector(excel_data, steady_state_time_spans)
    
    
    # excel_data_steady_state_reset_time_filtered = df_noise_cancelation(excel_data_steady_state_reset_time, method='convolution')
    excel_data_steady_state_filtered = df_noise_cancelation_for_time_spans(excel_data, steady_state_time_spans, method='convolution')
    
    # Defining df in which average values of data is availabel:
    df_col_names = excel_data_steady_state.columns
    df_col_names = df_col_names.tolist()
    time_heading = ['record_date_start [-]', 'record_date_end [-]', 'record_time_start [-]', 'record_time_end [-]', 't_start [sec]', 't_end [sec]']

    df_avg_cols = time_heading + df_col_names
    df_avg = pd.DataFrame([], columns=df_avg_cols)
    
    
    if steady_state_rows != []:
    
        average_data = []

        
        
        for st_st_row_span in steady_state_rows:
            mean_values = []
            strt_row = st_st_row_span[0]
            end_row = st_st_row_span[1]
            
            strt_date = excel_data['record_date [-]'].iloc[strt_row]
            end_date = excel_data['record_date [-]'].iloc[end_row]
            
            strt_time = excel_data['record_time [-]'].iloc[strt_row]
            end_time = excel_data['record_time [-]'].iloc[end_row]
            
            strt_t = excel_data['t [sec]'].iloc[strt_row]
            end_t = excel_data['t [sec]'].iloc[end_row]
            
            time_list = [strt_date, end_date, strt_time, end_time, strt_t, end_t, strt_date, strt_time, strt_t]
            
            for col in excel_data.columns:
                if col !='record_date [-]' and col !='record_time [-]' and col != 't [sec]':
                
                
                    try:
                        mean_value = excel_data[col].iloc[strt_row:end_row].mean()
                    except:
                        mean_value = 0
    #                 mean_values = np.append(mean_values, mean_value)
                    mean_values.append(mean_value)
            
            
            complete_list = time_list+mean_values
            average_data.append(complete_list)
            del complete_list
        df_avg = pd.DataFrame(average_data, columns=df_avg_cols)
        
    return excel_data, excel_data_steady_state, excel_data_steady_state_filtered, df_avg, steady_state_time_spans


# In[3]:


def name_changer(data_frame, excel_file_path):
    xls = pd.ExcelFile(excel_file_path)
    sensor_data = pd.read_excel(xls, 'Sensors Description')
    # Changing sensors' name to the tags
    for col_name in data_frame.columns:
        matches= sensor_data[sensor_data['Name'].str.match(col_name)]
        index = matches.index
        tags=sensor_data['Tag'][index]
        tag=tags.iloc[0]
        data_frame = data_frame.rename(columns={col_name : (tag)})  
    return data_frame


# In[4]:


def interpolate(xval, df, xcol, ycol):
    y_values = df[ycol]
    if y_values.dtype == 'object':
        df[ycol] = y_values
        y_values = df[ycol] 
        interapotated_value = y_values.iloc[0]
    else:
        interapotated_value = np.interp([xval], df[xcol], df[ycol])
    return interapotated_value


# In[5]:


def interpolate_dataframe(df, xcol, xval):
    columns = df.columns
    row_counter = 0
    for current_time in xval:
        row_values = np.array([])
        for col_name in columns:
            current_value = interpolate(current_time, df, xcol, col_name)
            row_values = np.append(row_values, current_value)
        if row_counter == 0:
            df_interpolated = pd.DataFrame(data=[row_values], columns=df.columns)
        else:
            df_row = pd.DataFrame(data=[row_values], columns=df.columns)
            df_interpolated = df_interpolated.append(df_row)
        row_counter = row_counter + 1
    return df_interpolated


# In[ ]:


def exp_data_plotter(df, x_label=None, y_label=None, time_span=None, monitor_time=None, maximum_difference_seconds=None, no_x_points=None, save_figure=None, save_figure_path=None, save_figure_resolution=None):
    if x_label is None:
        x_label = 't [sec]'
        
    if save_figure is None:
        save_figure = False
        
    if save_figure_resolution is None:
        save_figure_resolution = 1000
    
    
    x = df[x_label]
#     y_series = pd.Series([])
#     y_series = []
    if no_x_points is None:
        no_x_points = 10
        
    df_columns = df.columns
    if y_label is None:
        columns = df_columns.to_list()
#         columns.remove('t [sec]')
        columns.remove('record_date [-]')
        columns.remove('record_time [-]')
        
    else:
        columns = y_label
    if time_span is None:
        time_span = [df['t [sec]'].min(), df['t [sec]'].max()]
    if monitor_time is None:
        monitor_time = [];
    if maximum_difference_seconds is None:
        maximum_difference_seconds = 5; # Default value for time difference        
        
    df = df[(time_span[0] <= df[x_label])]
    df = df[(df[x_label] <= time_span[1])]
    x = df[x_label]
    if len(monitor_time) >= 1:
#         monitor_points_readings = np.empty([len(monitor_time),len(columns)], dtype=float, order='C')
        monitor_points_readings = np.empty([len(monitor_time),len(columns)], order='C')

    y_series = x
    for col_no in range(len(columns)):
        column_name = columns[col_no]

        y = df[column_name]
        data = []
        try:
            y = y.astype(str).astype(float)
            df[column_name] = y
        except:
            y = y

        if not y.dtype == 'object':
            y_series = pd.concat([y_series, y], axis = 1)
            fig, ax1 = plt.subplots(1,1,figsize=(14,5), dpi= 500)

            g = 0
            for i in range(len(x)):
                x0 = x.iloc[i]
                y0 = y.iloc[i]
                if i < (len(x)-1):
                    x1 = x.iloc[i+1]

                    td = x1 - x0
                    if td < maximum_difference_seconds:
                        data.append([x0,y0, g])
                    else:
                        data.append([x0,y0, g])
                        g+=1
                else:
                    data.append([x0,y0, g])

            df_1 = pd.DataFrame(data, columns=['x', 'y', 'group'])

            for i, dfg in df_1.groupby('group'):
                ax1.plot(dfg['x'], dfg['y'], c='b')            
                if x_label == 't [sec]':
#                     x_label_to_show = x_label
                    start_time = df["record_time [-]"].iloc [0] 
                    end_time = df["record_time [-]"].iloc [-1] 
                    x_label_to_show = x_label + ' (' + str(start_time) + '~' + str(end_time) + ')'
                else:
                    x_label_to_show = x_label
                ax1.set_xlabel(x_label_to_show, fontsize=16)
                ax1.tick_params(axis='x', rotation=0, labelsize=12)
                ax1.set_ylabel(columns[col_no],  fontsize=16)
                ax1.tick_params(axis='y', rotation=0, labelsize=12)
                ax1.grid(alpha=.4)
                
                x_show_values = np.linspace(x.iloc[0], x.iloc[-1], num=no_x_points)
                plt.xticks(x_show_values)
                
            if len(monitor_time) >= 1:
                monitor_counter = 0
                for monitor_second in monitor_time:
                    monitor_value = interpolate(monitor_second, df, x_label, columns[col_no])
                    label_value = '{:.3f}'.format(monitor_value[0])
                    monitor_points_readings[monitor_counter][col_no] = monitor_value[0]
                    
                    label = plt.annotate(label_value, (monitor_second, monitor_value),ha='center', fontsize=16)
                    ax1.vlines(x=monitor_second, ymin=y.min(), ymax=monitor_value, alpha=0.7, linewidth=2, ls = '--', color = 'black')
                    monitor_counter = monitor_counter + 1
                    
            if save_figure:
                save_fig_name = column_name.split('[')
                if len(save_fig_name) == 1: # meaning that the column name does not containg '['
                    save_fig_name = column_name
                    save_fig_name = save_fig_name.replace("/", "-")
                else:
                    save_fig_name = save_fig_name[0]
                    save_fig_name = save_fig_name[0:-1]
                    save_fig_name = save_fig_name.replace("/", "-")
                
                
                # Check whether the specified path exists or not
                isExist = os.path.exists(save_figure_path)
                if not isExist:
                  # Create a new directory because it does not exist 
                  os.makedirs(save_figure_path)
                save_fig(save_fig_name, save_figure_path, tight_layout=True, fig_extension="jpg", resolution=save_figure_resolution)                
                
            plt.show()
    

    if len(monitor_time) >= 1:
        y_dataframe = pd.DataFrame(monitor_points_readings, columns=columns)
        display(y_dataframe)
    else:
        y_dataframe = pd.DataFrame(y_series)
    return y_dataframe


# In[5]:


def data_plotter(df, x_label,  y_label=None, time_span=None, monitor_time=None, excel_file_path_for_sensors = None, variable_des = None):
    var_description = list()
    if excel_file_path_for_sensors is not None:
        df, var_des = variable_name_modifier(df, excel_file_path_for_sensors, label_with_tag = True, original_sensor_name = False)
    else:

        var_des = variable_des
    for name_seri in var_des:
        tag = name_seri[0]
        unit = name_seri[1]
        description = name_seri[2]
        var_description.append([tag + unit, description])
    x = df[x_label]
#     y_series = pd.Series([])
#     y_series = []
    df_columns = df.columns
    if y_label is None:
        columns = df_columns
    else:
        columns = y_label
    if time_span is None:
        time_span = [df['t [sec]'].min(), df['t [sec]'].max()]
    if monitor_time is None:
        monitor_time = [];
#     if maximum_difference_seconds is None:
    maximum_difference_seconds = 5; # Default value for time difference        
        
    df = df[(time_span[0] <= df[x_label])]
    df = df[(df[x_label] <= time_span[1])]
    x = df[x_label]
    
    y_series = x
    for col_no in range(len(columns)):
        column_name = columns[col_no]
        y = df[column_name]
        data = []
        try:
            y = y.astype(str).astype(float)
            df[column_name] = y
        except:
            y = y

        if not y.dtype == 'object':
            y_series = pd.concat([y_series, y], axis = 1)
            fig, ax1 = plt.subplots(1,1,figsize=(14,5), dpi= 500)

            g = 0
            for i in range(len(x)):
                x0 = x.iloc[i]
                y0 = y.iloc[i]
                if i < (len(x)-1):
                    x1 = x.iloc[i+1]

                    td = x1 - x0
                    if td < maximum_difference_seconds:
                        data.append([x0,y0, g])
                    else:
                        data.append([x0,y0, g])
                        g+=1
                else:
                    data.append([x0,y0, g])

            df_1 = pd.DataFrame(data, columns=['x', 'y', 'group'])

            # draw a plot
#             fig, ax = plt.subplots(1,1, figsize = (8,5))
            for i, dfg in df_1.groupby('group'):

                ax1.plot(dfg['x'], dfg['y'], c='b')            
                if x_label == 't [sec]':
#                     x_label_to_show = x_label
                    start_time = df["record_time [-]"].iloc [0] 
                    end_time = df["record_time [-]"].iloc [-1] 
                    x_label_to_show = x_label + ' (' + str(start_time) + '~' + str(end_time) + ')'
                else:
                    x_label_to_show = x_label
                ax1.set_xlabel(x_label_to_show, fontsize=16)
                ax1.tick_params(axis='x', rotation=0, labelsize=12)
                ax1.set_ylabel(columns[col_no],  fontsize=16)
                ax1.tick_params(axis='y', rotation=0, labelsize=12)
                ax1.grid(alpha=.4)

            if len(monitor_time) >= 1:
                for monitor_second in monitor_time:
                    monitor_value = interpolate(monitor_second, df, x_label, columns[col_no])
                    label_value = '{:.3f}'.format(monitor_value[0])
                    label = plt.annotate(label_value, (monitor_second, monitor_value),ha='center', fontsize=16)
                    ax1.vlines(x=monitor_second, ymin=y.min(), ymax=monitor_value, alpha=0.7, linewidth=2, ls = '--', color = 'black')
            idex_in_list = in_list(column_name,var_description)
            plot_title = var_description[idex_in_list][1]
            ax1.set_title(plot_title, fontsize=20)            
            plt.show()
            y_dataframe = pd.DataFrame(y_series)
    return y_dataframe


# In[ ]:


def cycle_performance_valuator(WN_df, LB_def, monitor_time=None):
    if monitor_time is None:
        monitor_time = [];
#     required parameter for cycle analysis are:
#  reference power, generated power, fuel mass flow - H2, fuel mass flow - CH4, rotational speed
# turbine outlet temperature, 
        
    


# In[ ]:


def load_data_frames_for_date(year, month, day, organized_data_path, sensor_file, weather_file):
    data_date = str(year) + '_' + str(month) + '_' + str(day)
    data_date_value = str(year) + '-' + str(month) + '-' + str(day)
    weather_df= pd.read_csv(weather_file)
#     print(weather_df)
    p_atm = 0.001 * weather_df[weather_df['datetime']==data_date_value]['sealevelpressure'].iloc[0]
    N_nom = 70000
    dfs = dict()
    path = organized_data_path + '/' + data_date
    my_list = os.listdir(path)
    
    no_data_sets = 0
    if 'WN' in my_list:
        WN_df, WN_dfs, WN_var_des = load_data_frames('WN',  data_date, organized_data_path, p_atm, sensor_file)
        WN_df['p_amb [bar]'] = p_atm
        if 'N_ref [%]' in WN_df.columns and 'N_ref [rpm]' not in WN_df.columns:
            WN_df['N_ref [rpm]'] = N_nom/100 * WN_df['N_ref [%]']
        if 'N_act [%]' in WN_df.columns and 'N_act [rpm]' not in WN_df.columns:
            WN_df['N_act [rpm]'] = N_nom/100 * WN_df['N_act [%]']
            
        WN_df = sensors_name_reorder(WN_df, sensor_file)
        dfs[no_data_sets] = WN_df
        no_data_sets += 1
    if 'LV' in my_list:
        LV_df, LV_dfs, LV_var_des = load_data_frames('LV',  data_date, organized_data_path, p_atm, sensor_file)
        LV_df['p_amb [bar]'] = p_atm
        if 'N_ref [%]' in LV_df.columns and 'N_ref [rpm]' not in LV_df.columns:
            LV_df['N_ref [rpm]'] = N_nom/100 * LV_df['N_ref [%]'] 
        if 'N_act [%]' in LV_df.columns and 'N_act [rpm]' not in LV_df.columns:
            LV_df['N_act [rpm]'] = N_nom/100 * LV_df['N_act [%]']   
        LV_df = sensors_name_reorder(LV_df, sensor_file)
        dfs[no_data_sets] = LV_df
        no_data_sets += 1
    if 'GA' in my_list:
        GA_df, GA_dfs, GA_var_des = load_data_frames('GA',  data_date, organized_data_path, p_atm, sensor_file)
        GA_df['p_amb [bar]'] = p_atm
        if 'N_ref [%]' in GA_df.columns and 'N_ref [rpm]' not in GA_df.columns:
            GA_df['N_ref [rpm]'] = N_nom/100 * GA_df['N_ref [%]']          
        if 'N_act [%]' in GA_df.columns and 'N_act [rpm]' not in GA_df.columns:
            GA_df['N_act [rpm]'] = N_nom/100 * GA_df['N_act [%]']   
        GA_df = sensors_name_reorder(GA_df, sensor_file)
        dfs[no_data_sets] = GA_df
        no_data_sets += 1   
    return dfs
        


# In[ ]:


def build_up_df(*dfs):
    df_counter = 0
    
    for df_no in range(len(dfs)):
        if df_no == 0:
            df_complete = dfs[df_no]
        else:
            df_complete = df_complete.append(dfs[df_no])
            
    return df_complete


# In[ ]:


def df_sensor_average_val(df, tol=None):
    
    df_temp = df.copy()
    sensor_names = df_temp.columns.to_list()
    
    
    if tol is None:
        tol = 0.5
        
    sensor_group = sensor_group_finder(sensor_names)
    columns = df_temp.columns
    group_values = dict()
    out_of_range_sensors = list()
    for row_no in range(len(df_temp)):
        for group_no in range(len(sensor_group)):
            values = np.array([])
            for sensor_name in sensor_group[group_no]:
                values = np.append(values, df_temp[sensor_name].iloc[row_no])
            average_value = np.mean(values)
            deviation = values - average_value
            rel_deviation = abs(deviation)/abs(values)
            
            # check if there is an out of range value:
            out_of_range_values = np.array([])
            for val_no in range(len(rel_deviation)):
                value = rel_deviation[val_no]
                if value > tol:
                    out_of_range_sensors.append(sensor_group[group_no][val_no])
                    out_of_range_values = np.append(out_of_range_values, values[val_no])
            values = np.setdiff1d(values,out_of_range_values)
            average_value = np.mean(values)
            snesor_tag, snesor_unit = tag_unit_separator(sensor_name)
            snesor_name_average = snesor_tag[:-2] + '_cal_avg ' + snesor_unit
            df_temp.loc[row_no, snesor_name_average] = average_value
    unique_out_of_range_sensors = []
    unique = [x for x in out_of_range_sensors if x not in unique_out_of_range_sensors and unique_out_of_range_sensors.append(x)]
    return df_temp, unique_out_of_range_sensors
        


# In[ ]:


def sensor_group_finder(sensor_names):

        
    sensor_tages = list()
    sensor_units = list()
    sensor_tages_length = list()

    for sensor_no in range(len(sensor_names)):
        snesor_tag, snesor_unit = tag_unit_separator(sensor_names[sensor_no])
        sensor_tages.append(snesor_tag)
        sensor_units.append(snesor_unit)
        sensor_tages_length.append(len(snesor_tag))
    
    sensor_group_counter = 0
    sensor_group = dict()
    
    for sensor_no_ref in range(len(sensor_names)):
        
        for sensor_no in range(len(sensor_names)):
            if sensor_tages_length[sensor_no_ref] == sensor_tages_length[sensor_no] and            sensor_units[sensor_no_ref] == sensor_units[sensor_no]:
                current_sensor_unit = ' ' + sensor_units[sensor_no_ref]
                both_numbers = False
                not_location_no = False
                try:
                    last_str_int_ref = int(sensor_tages[sensor_no_ref][-1])
                    last_str_int = int(sensor_tages[sensor_no][-1])
                except:
                    last_str_int_ref = []
                    last_str_int = []
                if last_str_int_ref != [] and last_str_int != []:
                    both_numbers = True

                if len(sensor_tages[sensor_no]) >= 2 and len(sensor_tages[sensor_no_ref]) >= 2:
                    if sensor_tages[sensor_no][-2] == '_' and sensor_tages[sensor_no_ref][-2] == '_':
                        not_location_no = True
                
                
                if sensor_tages[sensor_no_ref][:-1] == sensor_tages[sensor_no][:-1] and sensor_tages[sensor_no_ref] != sensor_tages[sensor_no] and                both_numbers and not_location_no:
                    if sensor_group_counter == 0: # this is the first time we find a match
                        sensor_group[sensor_group_counter] = [sensor_tages[sensor_no_ref] + current_sensor_unit, sensor_tages[sensor_no] + current_sensor_unit]
                        sensor_group_counter = sensor_group_counter + 1
                    else:
                        match_key = -1 
                        # check if there is a match group
                        for key, value in sensor_group.items():
                            if sensor_tages[sensor_no_ref] + current_sensor_unit in value or sensor_tages[sensor_no] in value:
                                match_key = key

                                
                        if match_key >= 0:
#                             sensor_group[match_key] = [sensor_tages[sensor_no_ref], sensor_tages[sensor_no]]
                            
                            if sensor_tages[sensor_no_ref] + current_sensor_unit not in sensor_group[match_key]:
                                sensor_group[match_key]. append(sensor_tages[sensor_no_ref] + current_sensor_unit)
                            elif sensor_tages[sensor_no] + current_sensor_unit not in sensor_group[match_key]:
                                sensor_group[match_key]. append(sensor_tages[sensor_no] + current_sensor_unit)
                            else:
                                pass
                        else:
                            sensor_group[sensor_group_counter] = [sensor_tages[sensor_no_ref] + current_sensor_unit, sensor_tages[sensor_no] + current_sensor_unit]
                            sensor_group_counter = sensor_group_counter + 1
    return sensor_group
        


# In[ ]:


def tag_unit_separator(snesor):
    snesor_name = snesor[:]
    if '[' in snesor_name:
        snesor_name_split = snesor_name.split('[')
        snesor_unit = snesor_name_split[1]
        snesor_unit = '[' + snesor_unit
        snesor_tag = snesor_name_split[0]
        snesor_tag = snesor_tag[0:-1]
    else:
        snesor_tag = snesor_name
        snesor_unit = '[-]'
    return snesor_tag, snesor_unit


# In[10]:


def load_data_frames(data_origin,  data_date, organized_data_path, p_atm, excel_file_path_for_sensors):
    file_path = organized_data_path + '/' + data_date + '/' + data_origin
    file_list_complete = list()
    file_list = list()
    for files in os.listdir(file_path):
        if not files[0] == '~':
            file_list_complete.append(files) 
    file_no = 0
    start_time_series = list()
    dfs = dict()
    for file_name in file_list_complete:
        file_no = file_no + 1  
        try:
            file_name_full_path = file_path + '/' + file_name 

#             print(file_name_full_path)
            exp_load = data_origin + "_df_" + str(file_no) + " = pd.read_excel(file_name_full_path)"
            exec(exp_load)
            temp_var, variable_description = eval('variable_name_modifier(' + data_origin + "_df_" + str(file_no) + ', excel_file_path_for_sensors, atmospheric_pressure=p_atm)')
            exp_modify =  data_origin + '_df_' + str(file_no) + ' = temp_var'
            exec(exp_modify)
            del temp_var
            df_temp = eval(data_origin + "_df_" + str(file_no) )
            start_time_for_df = eval(data_origin + "_df_" + str(file_no) + "['record_time [-]'].iloc[0]" )
            if start_time_for_df in start_time_series: # check if it is a redundant time span
                indd = start_time_series.index(start_time_for_df)
                indd = indd + 1
                exp_equality_dataframe = data_origin + "_df_" + str(indd) + ".equals(" + data_origin + "_df_" + str(file_no) + "):"
                if exp_equality_dataframe:
#                     print('Redundant data has been detected.')
                    exp_delete_dataframe = "del " + data_origin + "_df_" + str(file_no)
                    exec(exp_delete_dataframe)
                    file_no = file_no - 1
            else:
                exp_time_start = "start_time_series.append(start_time_for_df)"
                exec(exp_time_start)
            file_list.append(file_name) 
        except:
            file_no = file_no - 1       
    print ('          • '+ str(file_no) + " dataset(s) gathered for " + data_origin + ' and saved in the dictionary.')
#     Concat all dataframes
    exp_column_name = "column_names = " + data_origin + "_df_1.columns" 
    exec(exp_column_name)   
    complete_df = eval("pd.DataFrame(columns = column_names)" )
    sort_index = list()
    start_time_series_sorted = sorted(start_time_series)
    df_counter = 0
    file_list_updated = list()
    for st_time in start_time_series_sorted:
        ind = start_time_series.index(st_time)
        sort_index.append(ind)
        file_list_updated.append(file_list[ind])
        name = file_list[ind]
        ind = ind + 1
        temp_df = eval(data_origin + '_df_' + str(ind))
        exp_df_temp_to_dict = 'df_temp_to_dict = {"' + data_origin + "_df_" + str(ind) + '":temp_df, "' + data_origin + "_df_" + str(ind) + '_name": name }'
        df_temp_to_dict = eval(' {"' + data_origin + '_df_' + str(ind) + '":temp_df,"' + data_origin + '_df_' + str(ind) + '_name": name }')
        dfs.update(df_temp_to_dict)
        if df_counter == 0:
            complete_df = temp_df
        if df_counter > 0:
            start_time_previous_df = complete_df['record_time [-]'].iloc[0]
            end_time_previous_df = complete_df['record_time [-]'].iloc[-1]
            start_time_current_df = temp_df['record_time [-]'].iloc[0]
            end_time_current_df = temp_df['record_time [-]'].iloc[-1]
            # Check and see if there is an overlap bwn the time spans of the dataframes
            if start_time_current_df < end_time_previous_df:
                overlap_timespan = [start_time_current_df, end_time_previous_df]
                complete_df_1 = complete_df.loc[complete_df['record_time [-]'] < overlap_timespan[0]]
                complete_df_common = complete_df.loc[complete_df['record_time [-]'] >= overlap_timespan[0]]
                complete_df_common = complete_df_common.loc[complete_df['record_time [-]'] <= overlap_timespan[1]]
                complete_df_2 = complete_df.loc[complete_df['record_time [-]'] > overlap_timespan[0]]
                temp_df_common = temp_df.loc[temp_df['record_time [-]'] >= overlap_timespan[0]]
                temp_df_common = temp_df_common.loc[temp_df['record_time [-]'] <= overlap_timespan[1]]
                temp_df_2 = temp_df.loc[temp_df['record_time [-]'] > overlap_timespan[0]]
                df_common = complete_df_common.append(temp_df_common, ignore_index=True, sort=False)
                df_common = df_common.sort_values('record_time [-]')
                complete_df = complete_df_1.append(df_common, ignore_index=True, sort=False)
                complete_df = complete_df.append(temp_df_2, ignore_index=True, sort=False)
            else:                
                complete_df = complete_df.append(temp_df, ignore_index=True, sort=False)
            del temp_df
        df_counter = df_counter + 1
    complete_df = complete_df.sort_values('record_time [-]')
    complete_df.reset_index(drop=True, inplace=True)
    complete_df = recalculate_column(complete_df, 'record_time [-]' , 't [sec]')
    counter = 1
    for st_time in start_time_series_sorted:
        temp = eval('dfs["' + data_origin + '_df_' + str(counter) + '"]')
        time_array = temp["record_time [-]"]
        del temp
        temp = complete_df.loc[complete_df["record_time [-]"].isin(time_array)]
        exp_df_temp_to_dict = 'df_temp_to_dict = {"' + data_origin + "_df_" + str(counter) + '": temp}'
        df_temp_to_dict = eval('{"' + data_origin + '_df_' + str(counter) + '": temp}')
        dfs.update(df_temp_to_dict)
        del temp
        counter = counter + 1
    return complete_df, dfs, variable_description


# In[2]:


def recalculate_column(df, reference_column_name, modifying_column_name, begin_value = None):
    if begin_value is None:
        begin_value = 0
    r, c = df.shape
    rows = range(1, r, 1)
    mv = np.array([begin_value])
    for row_no in rows:
        val0 = df[reference_column_name].iloc[row_no-1]
        val0 = datetime.datetime.strptime(val0, "%H:%M:%S.%f")
        val1 = df[reference_column_name].iloc[row_no]
        val1 = datetime.datetime.strptime(val1, "%H:%M:%S.%f")
        val = val1 - val0
        val = val.total_seconds()
        mv = np.append(mv, val + mv[row_no-1])
    df[modifying_column_name] = mv
    return df


# In[ ]:


# def common_time_df_provider(df_1, df_2, x_label=None, reset_time=None):
def common_time_df_provider(dfs, x_label=None, reset_time=None):
    new_dfs = dict()
    if x_label is None:
        x_label = 'record_time [-]';
    if reset_time is None:
        reset_time = True;    
    
#     Finding the common timespan
    start_times = list()
    end_times = list()
    
    for df_no in range(len(dfs)):
        df = dfs[df_no]
        df_start_time = df[x_label].iloc[0]
        df_end_time = df[x_label].iloc[-1]
        
        if df_no == 0:
            start_times = [df_start_time]
            end_times = [df_end_time]
        else:
        
            start_times.append(df_start_time)
            end_times.append(df_end_time)

        del df
    start_times_sorted = sorted(start_times)
    end_times_sorted = sorted(end_times)
    common_time_span = [start_times_sorted[-1], end_times_sorted[0]]        
        
        
    for df_no in range(len(dfs)):
        df = dfs[df_no]
        df = df[(common_time_span[0] <= df[x_label])]
        df = df[(df[x_label] <= common_time_span[1])] 
        if reset_time is True:
            df['t [sec]'] = df['t [sec]'] - df['t [sec]'].iloc[0]
        new_dfs[df_no] = df
        del df
    return new_dfs, common_time_span    
        


# In[ ]:


# A fuction to adjust the frequency between two data frames that have the same begining and ending time and date, but different number of data collected in that time span
def frequency_adjustor(data_frames_dict):
    data_frames_dict_same_fr = dict()
    no_of_dfs = len(data_frames_dict)
#     Finding the shortest dataframe
    smallest_length = 1e10
    reference_df = pd.DataFrame([], columns=[])
    for df_no in range(no_of_dfs):
        if len(data_frames_dict[df_no]) < smallest_length:
            smallest_length = len(data_frames_dict[df_no])
            del reference_df
            reference_df = data_frames_dict[df_no]
    for df_no in range(no_of_dfs):
        df = data_frames_dict[df_no]
        if not pd.DataFrame.equals(df, reference_df):
            df_date_time = df.copy()
            df_time_wo_ms = np.array([])
            modified_date = df_date_time['record_date [-]'].iloc[0].replace("_", "-")
            df_date_time['record_date_time [-]'] = modified_date + ' ' + df_date_time['record_time [-]'] 
            df_date_time_float = np.array([])
            for row_no in range(len(df_date_time['record_date_time [-]'])):
                time_in_date_time_str = df_date_time['record_date_time [-]'].iloc[row_no]
                time_in_date_time = datetime.datetime.strptime(time_in_date_time_str, "%Y-%m-%d %H:%M:%S.%f")
                time_in_float = datetime_to_float(time_in_date_time)
                df_date_time_float = np.append(df_date_time_float, time_in_float)
            df_date_time['date_time_float'] = df_date_time_float
            
            new_df = pd.DataFrame([], columns = df.columns)
            for row_no in range(len(reference_df)):
                t1 = reference_df['record_date [-]'].iloc[row_no] + ' ' + reference_df['record_time [-]'].iloc[row_no]
                t1 = datetime.datetime.strptime(t1, "%Y_%m_%d %H:%M:%S.%f")
                t1_float = datetime_to_float(t1)
                t1 = interpolate(t1_float, df_date_time, 'date_time_float', 't [sec]')
                df_interpolated = interpolate_dataframe(df, 't [sec]', t1)
                df_interpolated['record_date [-]'] = reference_df['record_date [-]'].iloc[row_no]
                df_interpolated['record_time [-]'] = reference_df['record_time [-]'].iloc[row_no]
                df_interpolated['t [sec]'] = reference_df['t [sec]'].iloc[row_no]
                new_df = new_df.append(df_interpolated)
                del df_interpolated
                
            new_df = new_df.reset_index(drop=True)
            new_df = dataframe_dtype_modifier(new_df)
            data_frames_dict_same_fr[df_no] = new_df
        else:
            df = df.reset_index(drop=True)
            df = dataframe_dtype_modifier(df)            
            data_frames_dict_same_fr[df_no] = df
        del df
#     Building a data-frame that has all the data
    for df_no in range(len(data_frames_dict_same_fr)):
        if df_no == 0:
            agg_df = data_frames_dict_same_fr[df_no]
        else:
            curr_df = data_frames_dict_same_fr[df_no].copy()
            curr_df.drop(['record_date [-]', 'record_time [-]', 't [sec]', 'p_amb [bar]'], axis=1, inplace=True)
            agg_df = pd.concat([agg_df, curr_df], axis=1)
#             agg_df = pd.merge(agg_df, curr_df, on='p_amb [bar]', how='outer')


    return data_frames_dict_same_fr, agg_df


# In[ ]:


def dataframe_dtype_modifier(df, target_type=None, exception_columns=None):
    if target_type is None:
        target_type = 'float'
    if exception_columns is None:
        exception_columns = ['record_date [-]', 'record_time [-]']
    df_1 = df.copy()
    df_2 = df.copy()
    df_1.drop(exception_columns, axis=1, inplace=True)
    df_1 = df_1.astype(float)
    
    modified_df = pd.concat([df_2[exception_columns], df_1], axis=1)
    
    return modified_df


# In[ ]:


def cycle_variable_plotter_ordered(dataframes, excel_file_path_for_sensors, x_label, y_label=None, time_span=None, time_span_clock=None, monitor_time=None, maximum_difference_seconds=None, save_pics=None, no_x_points=None):
    ordered_cycle_dfs = dict()
    
    if save_pics is None:
        save_pics = True
    if no_x_points is None:
        no_x_points = 10
    new_dataframes = dict()
    var_description = list()   
    var_des = []
    for i in range(len(dataframes)):
        df_to_ext_desc = dataframes[i]
        df_to_ext_desc, df_desc = variable_name_modifier(df_to_ext_desc, excel_file_path_for_sensors, label_with_tag = True, original_sensor_name = False)
        var_des = var_des + df_desc
        del df_to_ext_desc, df_desc        
    for name_seri in var_des:
        tag = name_seri[0]
        unit = name_seri[1]
        description = name_seri[2]
        var_description.append([tag + unit, description])
    # Reading sensor names for cycle assessment from the excel file
    xls = pd.ExcelFile(excel_file_path_for_sensors)
    sensor_data = pd.read_excel(xls, 'Selected Sensors')
    if y_label is None:
        columns = sensor_data['Name']
    else:
        columns = y_label    
    for df_no in range(len(dataframes)):
        df = dataframes[df_no]
        df_columns = df.columns
        x = df[x_label]
        if time_span is None:
            if time_span_clock is None:
                time_span = [df['t [sec]'].min(), df['t [sec]'].max()]
            else:
                df_date_time = df.copy()
                df_time_wo_ms = np.array([])
                modified_date = df_date_time['record_date [-]'].iloc[0].replace("_", "-")
                df_date_time['record_date_time [-]'] = modified_date + ' ' + df_date_time['record_time [-]'] 
                df_date_time_float = np.array([])
                for row_no in range(len(df_date_time['record_date_time [-]'])):
                    time_in_date_time_str = df_date_time['record_date_time [-]'].iloc[row_no]
                    time_in_date_time = datetime.datetime.strptime(time_in_date_time_str, "%Y-%m-%d %H:%M:%S.%f")
                    time_in_float = datetime_to_float(time_in_date_time)
                    df_date_time_float = np.append(df_date_time_float, time_in_float)
                df_date_time['date_time_float'] = df_date_time_float
                t1 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[0]
                t1 = datetime.datetime.strptime(t1, "%Y_%m_%d %H:%M:%S")
                t1_float = datetime_to_float(t1)
                t2 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[1]
                t2 = datetime.datetime.strptime(t2, "%Y_%m_%d %H:%M:%S")            
                t2_float = datetime_to_float(t2)
                t1 = interpolate(t1_float, df_date_time, 'date_time_float', 't [sec]')
                t2 = interpolate(t2_float, df_date_time, 'date_time_float', 't [sec]')
                time_span = [t1[0], t2[0]]       
        else:
            if time_span_clock is not None:
                df_date_time = df.copy()
                df_time_wo_ms = np.array([])
                modified_date = df_date_time['record_date [-]'].iloc[0].replace("_", "-")
                df_date_time['record_date_time [-]'] = modified_date + ' ' + df_date_time['record_time [-]'] 
                df_date_time_float = np.array([])
                for row_no in range(len(df_date_time['record_date_time [-]'])):
                    time_in_date_time_str = df_date_time['record_date_time [-]'].iloc[row_no]
                    time_in_date_time = datetime.datetime.strptime(time_in_date_time_str, "%Y-%m-%d %H:%M:%S.%f")
                    time_in_float = datetime_to_float(time_in_date_time)
                    df_date_time_float = np.append(df_date_time_float, time_in_float)
                df_date_time['date_time_float'] = df_date_time_float
                t1 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[0]
                t1 = datetime.datetime.strptime(t1, "%Y_%m_%d %H:%M:%S")
                t1_float = datetime_to_float(t1)
                t2 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[1]
                t2 = datetime.datetime.strptime(t2, "%Y_%m_%d %H:%M:%S")            
                t2_float = datetime_to_float(t2)
                t1 = interpolate(t1_float, df_date_time, 'date_time_float', 't [sec]')
                t2 = interpolate(t2_float, df_date_time, 'date_time_float', 't [sec]')
                time_span = [t1[0], t2[0]] 
            else:
                time_span = time_span
        if monitor_time is None:
            monitor_time = [];
        if maximum_difference_seconds is None:
            maximum_difference_seconds = 5; # Default value for time difference         
        df = df[(time_span[0] <= df[x_label])]
        df = df[(df[x_label] <= time_span[1])]
        x = df[x_label]
        y_series = x
        columns = sensor_unit_adder(excel_file_path_for_sensors, 'Selected Sensors', 'Name', 'Tag', 'Unit')
        column_counter = 0
        for column_name in columns:
            # Check the availability of the column name in the current dataframe
            columns_of_df = df.columns.to_series()
            if columns_of_df.eq(column_name).any():
                ordered_cycle_dfs[column_counter] = df[['record_date [-]', 'record_time [-]', 't [sec]', column_name]].copy()
            column_counter = column_counter + 1
    for param_no in range(len(columns)):
        column_name = columns[param_no]

        if param_no in ordered_cycle_dfs:
            del df
            df = ordered_cycle_dfs[param_no]
            # Check the availability of the column name in the current dataframe
            columns_of_df = df.columns.to_series()
            if columns_of_df.eq(column_name).any():
                y = df[column_name]
                data = []
                try:
                    y = y.astype(str).astype(float)
                    df[column_name] = y
                except:
                    y = y
                if not y.dtype == 'object':
                    y_series = pd.concat([y_series, y], axis = 1)
                    fig, ax1 = plt.subplots(1,1,figsize=(14,5), dpi= 500)
                    g = 0
                    for i in range(len(x)):
                        x0 = x.iloc[i]
                        y0 = y.iloc[i]
                        if i < (len(x)-1):
                            x1 = x.iloc[i+1]
                            td = x1 - x0
                            if td < maximum_difference_seconds:
                                data.append([x0,y0, g])
                            else:
                                data.append([x0,y0, g])
                                g+=1
                        else:
                            data.append([x0,y0, g])
                    df_1 = pd.DataFrame(data, columns=['x', 'y', 'group'])
                    for i, dfg in df_1.groupby('group'):
                        ax1.plot(dfg['x'], dfg['y'], c='b')            
                        if x_label == 't [sec]':
        #                     x_label_to_show = x_label
                            start_time = df["record_time [-]"].iloc [0] 
                            end_time = df["record_time [-]"].iloc [-1] 
                            x_label_to_show = x_label + ' (' + str(start_time) + '~' + str(end_time) + ')'
                        else:
                            x_label_to_show = x_label
                        ax1.set_xlabel(x_label_to_show, fontsize=16)
                        ax1.tick_params(axis='x', rotation=0, labelsize=12)
                        ax1.set_ylabel(column_name,  fontsize=16)
                        ax1.tick_params(axis='y', rotation=0, labelsize=12)
                        ax1.grid(alpha=.4)
                        x_show_values = np.linspace(x.iloc[0], x.iloc[-1], num=no_x_points)
                        plt.xticks(x_show_values)
                    if len(monitor_time) >= 1:
                        for monitor_second in monitor_time:
                            monitor_value = interpolate(monitor_second, df, x_label, column_name)
                            label_value = '{:.3f}'.format(monitor_value[0])
                            label = plt.annotate(label_value, (monitor_second, monitor_value),ha='center', fontsize=16)
                            ax1.vlines(x=monitor_second, ymin=y.min(), ymax=monitor_value, alpha=0.7, linewidth=2, ls = '--', color = 'black')
                    idex_in_list = in_list(column_name,var_description)
                    plot_title = var_description[idex_in_list][1]
                    ax1.set_title(plot_title, fontsize=20)
                    if save_pics:
                        start_time = df["record_time [-]"].iloc [0] 
                        end_time = df["record_time [-]"].iloc [-1] 
                        directory = os.getcwd()
                        directory = directory.split('/')
                        mother_directory = '/'
                        for word in directory[0:-1]:
                            if word != '':
                                mother_directory = mother_directory + word + '/'
                        save_picture_path = mother_directory + 'Data Figures/' + df['record_date [-]'].iloc[0]+ '/Cycle Figures'
                        time_span_string = str(start_time) + '~' + str(end_time)
                        time_span_string = time_span_string.replace(":", "_")
                        save_picture_path = save_picture_path + '/' + time_span_string + '/'
                        time_span_string = '(' + time_span_string + ')'
                        save_fig_name = plot_title + time_span_string  
                        # Check whether the specified path exists or not
                        isExist = os.path.exists(save_picture_path)
                        if not isExist:
                          # Create a new directory because it does not exist 
                          os.makedirs(save_picture_path)
                        save_fig(save_fig_name, save_picture_path)
                    plt.show()
                    y_dataframe = pd.DataFrame(y_series)
    new_dataframes[df_no] = y_dataframe        

    current_df = ordered_cycle_dfs[param_no]
    data = []
    x = current_df['t [sec]']
    y = current_df[columns[param_no]]
    fig, ax1 = plt.subplots(1,1,figsize=(14,5), dpi= 500)
    g = 0

    for i in range(len(x)):
        x0 = x.iloc[i]
        y0 = y.iloc[i]
        if i < (len(x)-1):
            x1 = x.iloc[i+1]
            td = x1 - x0
            if td < maximum_difference_seconds:
                data.append([x0,y0, g])
            else:
                data.append([x0,y0, g])
                g+=1
        else:
            data.append([x0,y0, g])
        df_1 = pd.DataFrame(data, columns=['x', 'y', 'group'])
        for i, dfg in df_1.groupby('group'):
            ax1.plot(dfg['x'], dfg['y'], c='b')            
            if x_label == 't [sec]':
    #                     x_label_to_show = x_label
                start_time = df["record_time [-]"].iloc [0] 
                end_time = df["record_time [-]"].iloc [-1] 
                x_label_to_show = x_label + ' (' + str(start_time) + '~' + str(end_time) + ')'
            else:
                x_label_to_show = x_label
            ax1.set_xlabel(x_label_to_show, fontsize=16)
            ax1.tick_params(axis='x', rotation=0, labelsize=12)
            ax1.set_ylabel(column_name,  fontsize=16)
            ax1.tick_params(axis='y', rotation=0, labelsize=12)
            ax1.grid(alpha=.4)
            x_show_values = np.linspace(x.iloc[0], x.iloc[-1], num=no_x_points)
            plt.xticks(x_show_values)
        if len(monitor_time) >= 1:
            for monitor_second in monitor_time:
                monitor_value = interpolate(monitor_second, df, x_label, column_name)
                label_value = '{:.3f}'.format(monitor_value[0])
                label = plt.annotate(label_value, (monitor_second, monitor_value),ha='center', fontsize=16)
                ax1.vlines(x=monitor_second, ymin=y.min(), ymax=monitor_value, alpha=0.7, linewidth=2, ls = '--', color = 'black')
        idex_in_list = in_list(column_name,var_description)
        plot_title = var_description[idex_in_list][1]
        ax1.set_title(plot_title, fontsize=20)
        if save_pics:
            start_time = df["record_time [-]"].iloc [0] 
            end_time = df["record_time [-]"].iloc [-1] 
            directory = os.getcwd()
            directory = directory.split('/')
            mother_directory = '/'
            for word in directory[0:-1]:
                if word != '':
                    mother_directory = mother_directory + word + '/'
            save_picture_path = mother_directory + 'Data Figures/' + df['record_date [-]'].iloc[0]+ '/Cycle Figures'
            time_span_string = str(start_time) + '~' + str(end_time)
            time_span_string = time_span_string.replace(":", "_")
            save_picture_path = save_picture_path + '/' + time_span_string + '/'
            time_span_string = '(' + time_span_string + ')'
            save_fig_name = plot_title + time_span_string  
            # Check whether the specified path exists or not
            isExist = os.path.exists(save_picture_path)
            if not isExist:
              # Create a new directory because it does not exist 
              os.makedirs(save_picture_path)
            save_fig(save_fig_name, save_picture_path)
        plt.show()
        y_dataframe = pd.DataFrame(y_series)
    #     new_dataframes[df_no] = y_dataframe
    return ordered_cycle_dfs


# In[ ]:


def in_list(item,L):
    for i in L:
        if item in i:
            return L.index(i)
    return -1


# In[ ]:


def sensor_unit_adder(excel_path, exel_sheet, col_name_1, col_name_2, col_name_3):
    xls = pd.ExcelFile(excel_path)
    sensor_data = pd.read_excel(xls, exel_sheet)
    sensor_name_complete = pd.Series(dtype = object)
    sensor_name_1 = sensor_data[col_name_1]
    sensor_name_2 = sensor_data[col_name_2]
    for number in range(len(sensor_name_1)):
        sensor_name_complete = sensor_name_complete.append(pd.Series(sensor_name_2[number] + ' [' + sensor_data[col_name_3].iloc[number] + ']'), ignore_index = True)
    return sensor_name_complete


# In[ ]:



def save_fig(fig_id, path, tight_layout=True, fig_extension="jpg", resolution=2500):
    
    fig_id = str(fig_id)
    if path[-1] != '/':
        path = path + '/'
        
    if '/' in fig_id:
        fig_id = fig_id.replace('/', '-')  
        
    
    path = path + fig_id + '.' + fig_extension
    

    
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution, bbox_inches='tight')
    return


# In[ ]:


def datetime_to_float(d):
    return d.timestamp()


# In[ ]:


def model_results_plotting(df, x_col_name, y_col_name, plot_title, z_col_name=None, No_of_x_ticks=None):
    if No_of_x_ticks is None:
        no_x_points = 10
    else:
        no_x_points = No_of_x_ticks
    x = df[x_col_name]
    y = df[y_col_name]
    if z_col_name is not None:
        z = df[z_col_name]
    
    fig, ax1 = plt.subplots(1,1,figsize=(14,5), dpi= 500)
#     fig, ax1 = plt.subplots(1,1,figsize=(14,5), dpi= 500)

    ax1.tick_params(axis='x', rotation=0, labelsize=12)
    ax1.set_xlabel(x_col_name,  fontsize=16)
    ax1.set_ylabel(y_col_name,  fontsize=16)
    ax1.tick_params(axis='y', rotation=0, labelsize=12)
    ax1.grid(alpha=.4)
    # Plotting both the curves simultaneously
    plt.plot(x, y, color='b', label='model')
    if z_col_name is not None:
        plt.plot(x, z, color='r', label='model')

        
    x_show_values = np.linspace(x.iloc[0], x.iloc[-1], num=no_x_points)
    plt.xticks(x_show_values)
    
    ax1.set_title(plot_title, fontsize=20)
    plt.xlabel(x_col_name)
    plt.ylabel(y_col_name)
    plt.title(plot_title)
    # Adding legend, which helps us recognize the curve according to it's color
    plt.legend()
    
    directory = os.getcwd()
    directory = directory.split('/')
    mother_directory = '/'
    for word in directory[0:-1]:
        if word != '':
            mother_directory = mother_directory + word + '/'

    save_picture_path = mother_directory + 'Data Figures'
    save_picture_path = save_picture_path + '/Model_Results/'

    save_fig_name = plot_title
    # Check whether the specified path exists or not
    isExist = os.path.exists(save_picture_path)
    if not isExist:
      # Create a new directory because it does not exist 
        os.makedirs(save_picture_path)
    save_fig(save_fig_name, save_picture_path)              
    plt.show()

    return
    


# In[ ]:



def dataframe_signal_filter(dataframes, n=20, a=1, x_label=None, plot_figures=None, method='a'):
    b = [1.0 / n] * n
    
    new_dataframes = dict()
    if isinstance(dataframes, pd.DataFrame):
        temporary_df = dataframes.copy()
        del dataframes
        dataframes = {0:temporary_df}
        del temporary_df
        
    if plot_figures is None:
        plot_figures = True
    if x_label is None:
        x_label = 't [sec]'
    for df_no in range(len(dataframes)):
        df = dataframes[df_no]
        df_filtered = df.copy()
        df_filtered.drop(['record_date [-]', 'record_time [-]', 't [sec]'], axis=1, inplace=True)
        df_columns = df_filtered.columns
        
        for col_name in df_columns:
            y = df_filtered[col_name]
            if y.dtype == 'object':
                y = pd.to_numeric(y, errors='coerce')
            yy = lfilter(b,a,y)
            df_filtered[col_name] = yy
        df_filtered[['record_date [-]', 'record_time [-]', 't [sec]']] =  df[['record_date [-]', 'record_time [-]', 't [sec]']]
        new_dataframes[df_no] = df_filtered
        
    return new_dataframes
                
 


# In[ ]:


# A function to plot two similar dataframes, mainly to compare filtered and unfiltered data
def plot_dataframes(df_dict_1, df_dict_2, figure_saving_path, x_label=None, x_span=None, legend=None, save_figure=None, figure_res=None, scatter=None):
    if save_figure is None:
        save_figure is False
    if figure_res is None:
        figure_res = 'low'
        
    if legend is None:
        legend = []
        
    if scatter is None:
        scatter = True
   

    if x_label is None:
        if 't [sec]' in df_dict_1.columns:
            x_label = 't [sec]'
        else:
            x_label = 'Data Point'
    if isinstance(df_dict_1, pd.DataFrame):
        temporary_df = df_dict_1.copy()
        del df_dict_1
        df_dict_1 = {0:temporary_df}
        del temporary_df  
    if isinstance(df_dict_2, pd.DataFrame):
        temporary_df = df_dict_2.copy()
        del df_dict_2
        df_dict_2 = {0:temporary_df}
        del temporary_df          
        
    for df_no in range(len(df_dict_1)):
        df_1 = df_dict_1[df_no]
        df_2 = df_dict_2[df_no]
        df_1 ['Data Point'] = np.arange(0,len(df_1))
        df_2 ['Data Point'] = np.arange(0,len(df_2))
        
        
        
        if x_span is not None:
#             time_span = [df_1['t [sec]'].min(), df_1['t [sec]'].max()]    

            df_1 = df_1[(x_span[0] <= df_1[x_label])]
            df_1 = df_1[(df_1[x_label] <= x_span[1])]             
            df_2 = df_2[(x_span[0] <= df_2[x_label])]
            df_2 = df_2[(df_2[x_label] <= x_span[1])]           

        

        columns = df_1.columns

        comparing_dfs = {0:df_1, 1:df_2}
        comparing_x = [x_label, x_label]
        comparing_x_label = x_label
        comparing_no_of_x_ticks = 10
        comparing_legends = legend
        columns = columns.values.tolist()
        try:
            columns.remove('record_date [-]')
            columns.remove('record_time [-]')
        except:
            pass
                    
        for col_name in columns:
            if col_name != x_label:
                comparing_y = [col_name, col_name]
                comparing_y_label = col_name
                comparing_plot_title = col_name
                c_dfs =  multiple_results_plotting(comparing_dfs, comparing_x, comparing_y, comparing_legends, comparing_x_label, comparing_y_label, comparing_plot_title, figure_saving_path, res = figure_res, no_of_x_ticks=comparing_no_of_x_ticks, save_fig_opt=save_figure)

    
    
    return
 


# In[ ]:


def multiple_results_plotting(dfs, x_col_names, y_col_names, legends, x_label, y_label, plot_title, save_picture_path, res = 'high', no_of_x_ticks=None, save_fig_opt=None, scatter=None):
    if save_fig_opt is None:
        save_fig_opt = True
    if scatter is None:
        scatter = True
    
    
    fn = 25
    colors_list = ['mediumblue', 'crimson', 'darkgreen', 'tab:red', 'tab:cyan']
    
    common_dfs = dict()
    min_of_x = list()
    max_of_x = list()
    no_of_plots = len(dfs)
    
    if no_of_x_ticks is None:
        no_of_x_ticks = 10
        
    if res == 'high':
        resolution = 2500
    else:
        resolution = 500
    
    
    for df_no in range(no_of_plots):
        df_current = dfs[df_no]
        x_current = df_current[x_col_names[df_no]]
        min_of_x.append(x_current.iloc[0])
        max_of_x.append(x_current.iloc[-1])
    
    min_x_ref = max(min_of_x)
    max_x_ref = min(max_of_x)

        
    for df_no in range(no_of_plots):
        temp_def = dfs[df_no].copy()
        x_l = x_col_names[df_no]
        temp_def = temp_def[(min_x_ref<=temp_def[x_l])]
        temp_def = temp_def[(temp_def[x_l]<=max_x_ref)]
        common_dfs[df_no] = temp_def   
        del temp_def


    fig, ax = plt.subplots(1,1,figsize=(14,5), dpi= resolution)

    ax.set_xlabel(x_label, fontsize=16)
    ax.tick_params(axis='x', rotation=0, labelsize=12) 
    ax.set_ylabel(y_label, fontsize=16)
    ax.tick_params(axis='y', rotation=0, labelsize=12)    
    ax.grid(alpha=.4)

#     N = 10
    for df_no in range(no_of_plots):
        
        df = common_dfs[df_no]
        x = df[x_col_names[df_no]]
        y = df[y_col_names[df_no]]
        if y.dtype == 'object':
            y = pd.to_numeric(y, errors='coerce')        
        if scatter:
            plt.scatter(x, y, c=colors_list[df_no], marker='.', alpha=0.5, linewidths=1, edgecolors=colors_list[df_no])
        else:
            plt.plot(x, y, color=colors_list[df_no], label=legends[df_no], linewidth=2)
        
        x_show_values = np.linspace(x.iloc[0], x.iloc[-1], num=no_of_x_ticks)
        plt.xticks(x_show_values)
    
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    if len(legends) >= 1:
    
        ax.legend(legends,fontsize=fn,loc=2, prop={'size': 15})

    if save_fig_opt:

        
        save_fig_name = plot_title.split('[')
        if len(plot_title) == 1: # meaning that the name does not containg '['
            save_fig_name = plot_title
            save_fig_name = plot_title.replace("/", "-")
        else:
            save_fig_name = save_fig_name[0]
            save_fig_name = save_fig_name[0:-1]
            save_fig_name = save_fig_name.replace("/", "-")  
        # Check whether the specified path exists or not
        isExist = os.path.exists(save_picture_path)
        if not isExist:
          # Create a new directory because it does not exist 
          os.makedirs(save_picture_path)
        save_fig(save_fig_name, save_picture_path, tight_layout=True, fig_extension="jpg")                
    plt.show()
    return common_dfs
    


# In[ ]:


def df_time_span_provider(dataframes, time_span=None, time_span_clock=None):
    x_label='t [sec]'
    new_dataframes = dict()

    if isinstance(dataframes, pd.DataFrame):
        input_type = 'DataFrame'
        temporary_df = dataframes.copy()
        del dataframes
        dataframes = {0:temporary_df}
        del temporary_df  
    else:
        input_type = 'Dictionary'
    
   
    for df_no in range(len(dataframes)):
        df = dataframes[df_no]
        df_columns = df.columns
        x = df[x_label]
        if time_span is None:
            if time_span_clock is None:
                time_span = [df['t [sec]'].min(), df['t [sec]'].max()]
            else:
                df_date_time = df.copy()
                df_time_wo_ms = np.array([])
                modified_date = df_date_time['record_date [-]'].iloc[0].replace("_", "-")
                df_date_time['record_date_time [-]'] = modified_date + ' ' + df_date_time['record_time [-]'] 
                df_date_time_float = np.array([])
                for row_no in range(len(df_date_time['record_date_time [-]'])):
                    time_in_date_time_str = df_date_time['record_date_time [-]'].iloc[row_no]
                    time_in_date_time = datetime.datetime.strptime(time_in_date_time_str, "%d/%m/%Y %H:%M:%S")
                    time_in_float = datetime_to_float(time_in_date_time)
                    df_date_time_float = np.append(df_date_time_float, time_in_float)
                df_date_time['date_time_float'] = df_date_time_float
                t1 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[0]
                t1 = datetime.datetime.strptime(t1, "%d/%m/%Y %H:%M:%S")
                t1_float = datetime_to_float(t1)
                t2 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[1]
                t2 = datetime.datetime.strptime(t2, "%d/%m/%Y %H:%M:%S")            
                t2_float = datetime_to_float(t2)
                t1 = interpolate(t1_float, df_date_time, 'date_time_float', 't [sec]')
                t2 = interpolate(t2_float, df_date_time, 'date_time_float', 't [sec]')
                time_span = [t1[0], t2[0]]       
        else:
            if time_span_clock is not None:
                df_date_time = df.copy()
                df_time_wo_ms = np.array([])
                modified_date = df_date_time['record_date [-]'].iloc[0].replace("_", "-")
                df_date_time['record_date_time [-]'] = modified_date + ' ' + df_date_time['record_time [-]'] 
                df_date_time_float = np.array([])
                for row_no in range(len(df_date_time['record_date_time [-]'])):
                    time_in_date_time_str = df_date_time['record_date_time [-]'].iloc[row_no]
                    time_in_date_time = datetime.datetime.strptime(time_in_date_time_str, "%d/%m/%Y %H:%M:%S")
                    time_in_float = datetime_to_float(time_in_date_time)
                    df_date_time_float = np.append(df_date_time_float, time_in_float)
                df_date_time['date_time_float'] = df_date_time_float
                t1 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[0]
                t1 = datetime.datetime.strptime(t1, "%d/%m/%Y %H:%M:%S")
                t1_float = datetime_to_float(t1)
                t2 = df['record_date [-]'].iloc[0] + ' ' + time_span_clock[1]
                t2 = datetime.datetime.strptime(t2, "%d/%m/%Y %H:%M:%S")            
                t2_float = datetime_to_float(t2)
                t1 = interpolate(t1_float, df_date_time, 'date_time_float', 't [sec]')
                t2 = interpolate(t2_float, df_date_time, 'date_time_float', 't [sec]')
                time_span = [t1[0], t2[0]] 
            else:
                time_span = time_span
       
        df = df[(time_span[0] <= df[x_label])]
        df = df[(df[x_label] <= time_span[1])]
        df = df.reset_index(drop=True)
        
        new_dataframes[df_no] = df
#         display(df)
        del df
        
    if input_type == 'DataFrame':
        new_dataframes = new_dataframes[0]
            
    return new_dataframes
        
        


# In[ ]:


def df_snapshot_provider(dataframes, snap_time=None, snap_time_clock=None):
    x_label='t [sec]'
    new_dataframes = dict()
    
    if isinstance(dataframes, pd.DataFrame):
        input_type = 'DataFrame'
        temporary_df = dataframes.copy()
        del dataframes
        dataframes = {0:temporary_df}
        del temporary_df  
    else:
        input_type = 'Dictionary'
    
   
    for df_no in range(len(dataframes)):
        df = dataframes[df_no]
        df_columns = df.columns
        x = df[x_label]
        if snap_time is None:
            if snap_time_clock is None:
                snap_time = [df['t [sec]'].min(), df['t [sec]'].max()]
            else:
                df_date_time = df.copy()
                df_time_wo_ms = np.array([])
                modified_date = df_date_time['record_date [-]'].iloc[0].replace("_", "-")
                df_date_time['record_date_time [-]'] = modified_date + ' ' + df_date_time['record_time [-]'] 
                df_date_time_float = np.array([])
                for row_no in range(len(df_date_time['record_date_time [-]'])):
                    time_in_date_time_str = df_date_time['record_date_time [-]'].iloc[row_no]
                    time_in_date_time = datetime.datetime.strptime(time_in_date_time_str, "%d.%m.%Y %H:%M:%S")
                    time_in_float = datetime_to_float(time_in_date_time)
                    df_date_time_float = np.append(df_date_time_float, time_in_float)
                df_date_time['date_time_float'] = df_date_time_float
                t1 = df['record_date [-]'].iloc[0] + ' ' + snap_time_clock
                t1 = datetime.datetime.strptime(t1, "%d.%m.%Y %H:%M:%S")
                t1_float = datetime_to_float(t1)
                t2_float = t1_float + 2
                t1 = interpolate(t1_float, df_date_time, 'date_time_float', 't [sec]')
                t2 = interpolate(t2_float, df_date_time, 'date_time_float', 't [sec]')
                snap_time = [t1[0], t2[0]]       
        else:
            if snap_time_clock is not None:
                df_date_time = df.copy()
                df_time_wo_ms = np.array([])
                modified_date = df_date_time['record_date [-]'].iloc[0].replace("_", "-")
                df_date_time['record_date_time [-]'] = modified_date + ' ' + df_date_time['record_time [-]'] 
                df_date_time_float = np.array([])
                for row_no in range(len(df_date_time['record_date_time [-]'])):
                    time_in_date_time_str = df_date_time['record_date_time [-]'].iloc[row_no]
                    time_in_date_time = datetime.datetime.strptime(time_in_date_time_str, "%d.%m.%Y %H:%M:%S")
                    time_in_float = datetime_to_float(time_in_date_time)
                    df_date_time_float = np.append(df_date_time_float, time_in_float)
                df_date_time['date_time_float'] = df_date_time_float
                t1 = df['record_date [-]'].iloc[0] + ' ' + snap_time_clock
                t1 = datetime.datetime.strptime(t1, "%d.%m.%Y %H:%M:%S")
                t1_float = datetime_to_float(t1)
                t2_float = t1_float + 2
                t1 = interpolate(t1_float, df_date_time, 'date_time_float', 't [sec]')
                t2 = interpolate(t2_float, df_date_time, 'date_time_float', 't [sec]')
                snap_time = [t1[0], t2[0]] 
            else:
                snap_time = [snap_time, snap_time+2]
                

        df = df[(snap_time[0] <= df[x_label])]
        df = df[(df[x_label] <= snap_time[1])]
        df = df.reset_index(drop=True)
        
        df = df.loc[[0]] # droping all rows except for the first one
        
        new_dataframes[df_no] = df
        display(df)
        del df
        
    if input_type == 'DataFrame':
        new_dataframes = new_dataframes[0]
            
    return new_dataframes
        
        


# In[ ]:


def save_df(df, file_name, ext='.csv', date=None):
    
    if date is None:
        date = df['record_date [-]'].iloc[0]
    
    directory = os.getcwd()
    directory = directory.split('/')
    mother_directory = '/'
    for word in directory[0:-1]:
        if word != '':
            mother_directory = mother_directory + word + '/'

    save_table_path = mother_directory + 'Results/' + str(date)
    save_table_path = save_table_path + '/Data Frames/'
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
 


# In[ ]:


def save_df_excel(df, file_name, sheet_name, date=None):
    
    if date is None:
        date = df['record_date [-]'].iloc[0]
    
    directory = os.getcwd()
    directory = directory.split('/')
    mother_directory = '/'
    for word in directory[0:-1]:
        if word != '':
            mother_directory = mother_directory + word + '/'

    save_table_path = mother_directory + 'Results/' + str(date)
    save_table_path = save_table_path + '/Data Frames/'
    isExist = os.path.exists(save_table_path)
    if not isExist:
      # Create a new directory because it does not exist 
      os.makedirs(save_table_path)        
    
    filepath = save_table_path + file_name +'.xlsx'
    if not os.path.exists(filepath):
        df.to_excel(filepath, sheet_name=sheet_name)

    # Otherwise, add a sheet. Overwrite if there exists one with the same name.
    else:
        with pd.ExcelWriter(filepath, engine='openpyxl', if_sheet_exists='replace', mode='a') as writer:
            df.to_excel(writer, sheet_name=sheet_name)
        
    print('The data-frame is saved in: ' + save_table_path + file_name +'.xlsx')
    
    return
        
 


# In[ ]:


def modify_simplified_steady_state(df, tol, ref_col=None, filtered_data=None):
    df_temp = df.copy()
    if ref_col is None:
        ref_col = 'P_ref [kW]'
    if filtered_data is None:
        filtered_data = False
        
    ref_col_name = ref_col[:]
    ref_col_split = ref_col_name.split('[')
    ref_col_unit = ref_col_split[1]
    ref_col_unit = '[' + ref_col_unit
    ref_col_name = ref_col_split[0]
    ref_col_name = ref_col_name[0:-1]
    st_col_name = ref_col_name + '_steady_state ' + ref_col_unit   
    
    if filtered_data:
        st_col_name = ref_col_name + '_filtered_steady_state ' + ref_col_unit   
    
    st_rows = df_temp[df_temp['transient']==0].index.tolist()
    st_vals = df_temp[st_col_name].iloc[st_rows].tolist()
    
    unique_st_vals = []
    unique = [x for x in st_vals if x not in unique_st_vals and unique_st_vals.append(x)]
    val_count=list()
    for value in unique_st_vals:
        repeated_times = (df_temp[st_col_name] == value).sum()
        val_count.append(repeated_times)
    new_st_vals = close_value_finder(unique_st_vals,val_count,tol)
    st_rows = np.array([])

    for index in range(len(unique_st_vals)):
        rows = df_temp.loc[df_temp[st_col_name]==unique_st_vals[index]].index
        df_temp.loc[rows,st_col_name] = new_st_vals[index]
        st_rows = np.append(st_rows, rows, axis=None)
        
    for counter in range(len(st_rows)):
        if counter > 0:
            
            if st_rows[counter]-st_rows[counter-1]>1 and abs(df_temp['t [sec]'].iloc[int(st_rows[counter])]-df_temp['t [sec]'].iloc[int(st_rows[counter-1])])<20 and abs(df_temp[st_col_name].iloc[int(st_rows[counter])]-df_temp[st_col_name].iloc[int(st_rows[counter-1])])<tol:
                df_temp.loc[range(int(st_rows[counter-1]),int(st_rows[counter])), 'transient'] = 0
                df_temp.loc[range(int(st_rows[counter-1]),int(st_rows[counter])),st_col_name] = df_temp[st_col_name].iloc[int(st_rows[counter-1]-1)]
        df_temp[st_col_name].iloc[rows] = new_st_vals[index]
    
    return df_temp

    
    
    
    
    


# In[2]:


def dataframe_summary_provider(df):
    
    
    df_temp = df.copy()    

    no_of_st_spans, st_span_start_t, st_span_end_t, st_span_start_time, st_span_end_time = steady_state_time_span_extractor(df_temp)
   
    summary_dataframe = pd.DataFrame([], columns=[])
    for span_no in range(no_of_st_spans):
        start_val = st_span_start_t[span_no]
        end_val = st_span_end_t[span_no]
        
        df_temp_avg = df_avg_cal(df_temp, 't [sec]', start_val, end_val)
        
        df_temp_avg = df_temp_avg.to_frame()
        df_temp_avg = df_temp_avg.T
        
        df_temp_avg.drop('t [sec]', inplace=True, axis=1)        
        df_temp_avg.insert(0, 'start_t [sec]', st_span_start_time[span_no])
        df_temp_avg.insert(1, 'end_t [sec]', st_span_end_time[span_no])
        df_temp_avg.insert(2, 'start_time [-]', start_val)
        df_temp_avg.insert(3, 'end_time [-]', end_val)        
        summary_dataframe = pd.concat([summary_dataframe, df_temp_avg], ignore_index=True, sort=False)

        del df_temp_avg
          
    
    table_data_frame_columns = ['start_time [-]',  'end_time [-]','start_t [sec]', 'end_t [sec]']

    table_data_frame = summary_dataframe[table_data_frame_columns]
    
    display(table_data_frame)
    
    return summary_dataframe, table_data_frame, st_span_start_t, st_span_end_t


# In[ ]:


def df_avg_cal(df, x_label, start_val, end_val):
    df_temp = df.copy()
    
    idx_start = df_temp[x_label].sub(start_val).abs().idxmin()
    idx_end = df_temp[x_label].sub(end_val).abs().idxmin()
    
#     focus_avg = df[ref_col].iloc[starting_row_in_df:ending_row_in_df].mean(axis=0)
    focus_avg = df_temp.iloc[idx_start:idx_end].mean(axis=0)
    
    return focus_avg
        


# In[ ]:


def steady_state_time_span_extractor(df):
    df_temp = df.copy()    
    no_of_st_spans = 0
    cursor_in_steady = 0
    cursor_in_transient = 0
    steady_span_start_time = list()
    steady_span_end_time = list()
    
    steady_span_start_t = np.array([])
    steady_span_end_t = np.array([])
    for row_no in range(len(df_temp)):
        if df_temp['transient'].iloc[row_no] == 0: 
            if cursor_in_steady == 0:
                no_of_st_spans = no_of_st_spans + 1
                cursor_in_steady = 1
                cursor_in_transient = 0
                steady_span_start_time.append(df_temp['record_time [-]'].iloc[row_no])
                steady_span_start_t = np.append(steady_span_start_t, df_temp['t [sec]'].iloc[row_no])
            else:
                pass
        else: # df_temp['transient'].iloc[row_no] == 1
            cursor_in_steady = 0
            if cursor_in_transient == 0:
                steady_span_end_time.append(df_temp['record_time [-]'].iloc[row_no-1])
                steady_span_end_t = np.append(steady_span_end_t, df_temp['t [sec]'].iloc[row_no-1])
                cursor_in_transient = 1
    if len(steady_span_start_t) - len(steady_span_end_t) == 1: # this means that the last part of the data is steady state, so we have to add the ending time to it
        steady_span_end_time.append(df_temp['record_time [-]'].iloc[-1])
        steady_span_end_t = np.append(steady_span_end_t, df_temp['t [sec]'].iloc[-1])

    
    return no_of_st_spans, steady_span_start_t, steady_span_end_t,  steady_span_start_time, steady_span_end_time
            
       


# In[ ]:


def close_value_finder(ref_values, value_count, tol):
    values = ref_values.copy()
    cls_val_indicator = 1

    while cls_val_indicator != 0:
        for index in range(len(values)):
            if abs(values[index] - values[index-1]) < tol and abs(values[index] - values[index-1])>0.000001:
                new_val = (values[index]*value_count[index] + values[index-1]*value_count[index-1])/(value_count[index]+value_count[index-1])
                values[index-1] = new_val
                values[index] = new_val
        cls_val_indicator = close_value_indicator(values, tol)
    return values
    

        
    
def close_value_indicator(values, tol):
    cls_val_indicator = 0
    for index in range(len(values)):
        if index > 0:
            if abs(values[index] - values[index-1]) < tol and abs(values[index] - values[index-1])>0.000001:
                cls_val_indicator = 1
    return cls_val_indicator
            


# In[ ]:


# This function adds a column to the dataframe by the name ref_col+steady_state
# In this column in transient time-spans the actual values from the ref_col is used and for 
# steady state time_spans the average values are used. 
def simplified_steady_state(df, ref_col=None, filtered_data=None):
    df_temp = df.copy()
    if ref_col is None:
        ref_col = 'P_ref [kW]'
        
    if filtered_data is None:
        filtered_data = False
        
    ref_col_name = ref_col[:]
    ref_col_split = ref_col_name.split('[')
    ref_col_unit = ref_col_split[1]
    ref_col_unit = '[' + ref_col_unit
    ref_col_name = ref_col_split[0]
    ref_col_name = ref_col_name[0:-1]
    st_col_name = ref_col_name + '_steady_state ' + ref_col_unit
    
    if filtered_data:
        st_col_name = ref_col_name + '_filtered_steady_state ' + ref_col_unit
        new_ref_col = ref_col_name + '_filtered ' + ref_col_unit
    else:
        new_ref_col = ref_col
        
    
        
    df_temp[st_col_name] = df_temp[new_ref_col]
    st_arr = np.array([])
    st_val = np.array([])
    st_rows = np.array([])

    for row_no in range(len(df_temp)):
        
        if df_temp['transient'].iloc[row_no] == 0:
            st_rows = np.append(st_rows, row_no, axis=None)
            st_arr = np.append(st_arr, df_temp[new_ref_col].iloc[row_no], axis=None)
        else: # df_temp['transient'].iloc[row_no] == 1
            if len(st_arr)>0:
                average_st = st_arr.mean(axis=0)
                st_rows = list(map(round, st_rows))
                df_temp.loc[st_rows,st_col_name] = average_st

                st_arr = np.array([])
                st_rows = np.array([])
    return df_temp
        


# In[2]:


def steady_state_data_extractor(df, ref_col=None, filter_data=None):
    df_temp = df.copy()
    
#     print(ref_col)
    
    if ref_col is None:
        ref_col = 'P_ref [kW]'
        
    if filter_data is None:
        filter_data = False
        
    
#     this combination seems to work: tol = 2, time_focus = 10, t_min_steady_state = 20
    tol = 4 # same unit as ref_col
    time_focus = 20 # sec
    t_min_steady_state = 100 # this is the time assumed to be too short to be between two transient time spans.

    
    if filter_data:
        ref_col_name = ref_col[:]
        ref_col_split = ref_col_name.split('[')
        ref_col_unit = ref_col_split[1]
        ref_col_unit = '[' + ref_col_unit
        ref_col_name = ref_col_split[0]
        ref_col_name = ref_col_name[0:-1]
        filter_col_name = ref_col_name + '_filtered ' + ref_col_unit
        y = df_temp[reference_column]
        smoother = ConvolutionSmoother(window_len=10, window_type='ones')
        smoother.smooth(y)
        df_temp[filter_col_name] = smoother.smooth_data[0]
        new_ref_col = filter_col_name
    else:
        new_ref_col = ref_col
    
    data_record_time = abs(df_temp['t [sec]'].iloc[0] - df_temp['t [sec]'].iloc[1])
    no_row_min_steady_state = round(t_min_steady_state/data_record_time)
    
    df_temp, dev_col_name = column_deviation(df_temp, new_ref_col, time_focus)
    
    
    df_temp['transient'] = np.where(df_temp[dev_col_name]>abs(tol), 1, 0)
    df_temp['transient'] = np.where(df_temp[dev_col_name]<-abs(tol), 1, df_temp['transient'])
    transient_rows = df_temp[df_temp['transient'] == 1].index.tolist()
    transient_time_spans = list()
    counter = 0
    modified_transient_rows = np.array([])
    for counter in range(len(transient_rows)):
        row_no = transient_rows[counter]
        if counter == 0:
            modified_transient_rows = np.append(modified_transient_rows, int(row_no), axis=None)
        else:
            if row_no - modified_transient_rows[-1] == 1: 
                modified_transient_rows = np.append(modified_transient_rows, int(row_no), axis=None)
            elif row_no - modified_transient_rows[-1] <= no_row_min_steady_state: # seems that the fuction didn't get 1 row by mistake, and we have to correct that
                a=range(int(modified_transient_rows[-1]) ,row_no+1,1)
                modified_transient_rows = np.append(modified_transient_rows, range(int(modified_transient_rows[-1]+1) ,int(row_no+1),1), axis=None)
            else: # row_no - modified_transient_rows[-1] > no_row_min_steady_state
                modified_transient_rows = np.append(modified_transient_rows, int(row_no), axis=None)
    modified_transient_rows = list(map(round, modified_transient_rows))
    df_temp.loc[modified_transient_rows, 'transient'] = 1
    df_steady_state =  df_temp[df_temp['transient'] == 0]

    return df_temp, df_steady_state, modified_transient_rows


# In[ ]:


def column_deviation(df, ref_col, time_focus):
    df_temp = df.copy()
    ref_col_name = ref_col[:]
    ref_col_split = ref_col_name.split('[')
    ref_col_unit = ref_col_split[1]
    ref_col_unit = '[' + ref_col_unit
    ref_col_name = ref_col_split[0]
    ref_col_name = ref_col_name[0:-1]
    dev_col_name = ref_col_name + '_deviation ' + ref_col_unit
    dev_col_val = np.array([])
    
    # Calculation of number of rows for the specifid time_tol
    data_record_time = abs(df['t [sec]'].iloc[0] - df['t [sec]'].iloc[1])
    no_row_time_focus = round(time_focus/data_record_time)
    no_row_df = len(df)
    no_row_focus =  math.floor(no_row_df/no_row_time_focus)
    remaining_rows = no_row_df - no_row_focus * no_row_time_focus
    
    for focus_no in range(no_row_focus):
        starting_row_in_df = focus_no * no_row_time_focus 
        ending_row_in_df = starting_row_in_df + no_row_time_focus - 1
        
        focus_avg = df[ref_col].iloc[starting_row_in_df:ending_row_in_df].mean(axis=0)
        for row_no_in_focus in range(no_row_time_focus):
            row_no_in_df = focus_no * no_row_time_focus + row_no_in_focus
            dev_col_val = np.append(dev_col_val,df[ref_col].iloc[row_no_in_df]-focus_avg, axis=None)
    
    remaining_row_no = range(no_row_df - remaining_rows , no_row_df, 1)

    focus_avg = df[ref_col].iloc[no_row_df - remaining_rows:no_row_df - 1].mean(axis=0)
    for row_no_in_df in remaining_row_no:
        dev_col_val = np.append(dev_col_val,df[ref_col].iloc[row_no_in_df]-focus_avg, axis=None)
        
    df_temp[dev_col_name] = dev_col_val
    
    return df_temp, dev_col_name
    
    
 
    


# In[22]:


from terminaltables import AsciiTable

def print_table(df, desired_col_name=None, desired_perc=None):
    df_temp = df.copy()
    
    if desired_col_name is None:
        desired_col_name = df_temp.columns
    if desired_perc is None:
        desired_perc = np.repeat(2, len(desired_col_name), axis=0)
    
    col_counter = 0
    for col_name in df_temp.columns:
        if df_temp[col_name].dtype == 'float':
#             df_temp[col_name] = np.round(df_temp[col_name] , decimals =1)
            df_temp[col_name] = df_temp[col_name].round(decimals=desired_perc[col_counter])

        
        col_counter = col_counter + 1

    
    
    table_data = df_temp.values.tolist()

    
    from tabulate import tabulate
    print(tabulate(table_data, desired_col_name, tablefmt="grid"))
    
    


# In[ ]:


def filter_convolution_smoother(y):
    smoother = ConvolutionSmoother(window_len=10, window_type='ones')
    smoother.smooth(y)
    y_filtered = smoother.smooth_data[0]
    return y_filtered


# In[ ]:


def averaging(t,f):
    
    f_mean = f.mean()
    f_mean_signal = np.repeat(f_mean, len(f), axis=0)
#     print(f)
#     print(f_mean)
    return f_mean_signal


# In[ ]:


def ending(t,f):
    
    f_end = f.iloc[-1]
    f_end_signal = np.repeat(f_end, len(f), axis=0)
#     print(f)
#     print(f_mean)
    return f_end_signal


# In[ ]:


def filter_FFT(t,f):
    
    # Compute the Fast Fourier Transform (FFT)
    n = len(t)
    dt = 0.001

    fhat = np.fft.fft(f, n)          # Compute the FFT
    PSD = fhat * np.conj(fhat) / n     # Power spectrum
    freq = (1/(dt*n)) * np.arange(n) # Create x-axis of frequencies
    L = np.arange(1,np.floor(n/2),dtype='int')


    treshold = 100
    # Use the PSD to filter out noise
    indices = PSD > treshold       # Find all freqs with larger power
    PSDclean = PSD * indices  # Zero out all others
    fhat = indices * fhat     # Zero out small Fourier coeffs in Y
    ffilt = np.fft.ifft(fhat) # Inverse FFt for filtered time signal


    return ffilt


# In[ ]:


def df_noise_cancelation(df, y_label=None, method=None):
    df_temp = df.copy()
    
    if y_label is None:
        parameters = df_temp.columns.to_list()
        try:
            parameters.remove('record_date [-]')
        except:
            pass
        try:
            parameters.remove('record_time [-]')
        except:
            pass        
        try:
            parameters.remove('t [sec]') 
        except:
            pass        
               
    else:
        parameters = y_label
        
        
    if method is None:
        mode = 'convolution'
    else:
        mode = method

    x = df_temp['t [sec]']
    parameter_no = 0
    for parameter_name in parameters:
        y = df_temp[parameter_name]
        try:
            if mode == 'convolution':
                y_filtered = filter_convolution_smoother(y)
            elif mode == 'FFT':
                y_filtered = filter_FFT(x,y)
            elif mode == 'avg' or  mode == 'averag' or  mode == 'averaging':
                y_filtered = averaging(x,y)
            elif mode == 'end':
                y_filtered = ending(x,y)

        except:
            y_filtered = y
        
        df_temp.drop(labels=parameter_name, axis=1, inplace=True)
        df_temp.insert(parameter_no, parameter_name, y_filtered)

    
        parameter_no = parameter_no + 1

    return df_temp 
    
    


# In[ ]:


def modify_date_time_col(df, col_name):
    # This function changes the data frame with date/time to 3 columns: date, time (clock) and elapsed time
    df_temp = df.copy()
    
    date_column = list()
    clock_column = list()
    time_column = np.empty(len(df_temp))
    for row_no in range(len(df_temp)):
        date_clock= str(df[col_name].iloc[row_no])
        date_clock_split = date_clock.split(' ')
        
        split_count = 0
        for split_count in range(len(date_clock_split)):
            splitted_part = date_clock_split[split_count]
            if splitted_part != ' ' and splitted_part != '':
                break
        
        date = str(date_clock_split[split_count])
        clock = str(date_clock_split[split_count+1])

        
        # unite the date format:
        try:
            date_format = datetime.datetime.strptime(date, "%d.%m.%Y")
        except:
            try:
                date_format = datetime.datetime.strptime(date, "%m/%d/%Y")
                date_split = date.split('/')
                date_m = date_split[0]
                date_d = date_split[1]
                date_y = date_split[2]
                
                date = date_d + '.' + date_m + '.' + date_y
                
                
            except:
                try:
                    date_format = datetime.datetime.strptime(date, "%Y-%m-%d")
                    date_split = date.split('-')
                    date_m = date_split[1]
                    date_d = date_split[2]
                    date_y = date_split[0]

                    date = date_d + '.' + date_m + '.' + date_y                
                
                
                except:
                    print('Check the date format')
                    print(date)
            
        date_column.append(date)
        clock_column.append(clock)
        if row_no == 0:
            clock_begin = clock
            
            try:
                clock_begin = datetime.datetime.strptime(clock_begin, "%H:%M:%S")
                include_seconds = True
            except:
                clock_begin = datetime.datetime.strptime(clock_begin, "%H:%M")
                include_seconds = False
            time_column[0] = 0
        else: 
            if include_seconds:

                clock_in_df = clock
                clock = datetime.datetime.strptime(clock, "%H:%M:%S")
                delta_time = clock - clock_begin
                time_column[row_no] = str(delta_time.total_seconds())
                if time_column[row_no] < time_column[row_no-1]: # meaning that there is a change in clock format (from 24h based to 12 hours based)
                    clock_split = str(clock_in_df).split(':')
                    hour = int(clock_split[0]) + 12
                    clock = str(hour)+':'+clock_split[1]+':'+clock_split[2]
                    clock = datetime.datetime.strptime(clock, "%H:%M:%S")
                    delta_time = clock - clock_begin
                    time_column[row_no] = str(delta_time.total_seconds())
            else:
                time_column = df['position']
                    
                    
    df_temp.drop(labels=col_name, axis=1, inplace=True)
    df_temp.insert(0, 'record_date [-]', date_column)
    df_temp.insert(1, 'record_time [-]', clock_column)
    df_temp.insert(2, 't [sec]', time_column)
    return df_temp    
    
    


# In[ ]:


def data_process_pipeline(year, month, day, organized_data_path, sensor_file, weather_file):
    data_date = str(year) + '_' + str(month) + '_' + str(day)

    print('Extracting data for '+ data_date + '...')
    dfs_dict = load_data_frames_for_date(year, month, day, organized_data_path, sensor_file,weather_file )
    print ('Data frames have been loaded and it is accessible in a dictionary as the first output of the pipeline.')
    
    print('Extracting common time spans where all data acquisition systems recorded data...')
    time.sleep(0.1)
    dfs_dict_common, common_time_span = common_time_df_provider(dfs_dict)
    print('The common data has been identified from '+ str(common_time_span[0]) + ' to ' + str(common_time_span[1]) + '.')
    print('The dataframes it is accessible in a dictionary as the second output of the pipeline.')
    
    print('Adjusting frequency of the commom data...')
    dfs_dict_common_same_frequency, dfs_common_same_frequency = frequency_adjustor(dfs_dict_common)
    dfs_common_same_frequency = sensors_name_reorder(dfs_common_same_frequency, sensor_file)
    dfs_common_same_frequency,_= df_sensor_average_val(dfs_common_same_frequency)
    print('The dataframe with adjusted frequency is provided as the third output of the pipeline.')
    
    
    print('Analyzing data to differentiate steady-state and transient time spans.')
    reference_column = 'P_ref [kW]'
    df = dfs_common_same_frequency.copy()
    use_filter_data = False
    
    df, df_st, ts = steady_state_data_extractor(df, ref_col=reference_column, filter_data=use_filter_data)
    df_simplified_steady_state = simplified_steady_state(df, filtered_data=use_filter_data)
    tol_var = 5
    df_simplified_steady_state = modify_simplified_steady_state(df_simplified_steady_state, tol_var, filtered_data=use_filter_data)
    df_simplified_steady_state, df_simplified_steady_state_st, ts = steady_state_data_extractor(df_simplified_steady_state, ref_col='P_ref_steady_state [kW]', filter_data=use_filter_data)

    
    print('The stady-state and transient behaviour is identified based on the data gathered for '+ reference_column + '.')

    
    df_simplified_steady_state_avg, df_simplified_steady_state_short,  st_span_start_t, st_span_end_t = dataframe_summary_provider(df_simplified_steady_state, sensor_file)
    print('A dataframe averaging all values in steady state timespans is provided as the fourth output of the pipeline.')
    print('Summary of data collected for '+ data_date + 'is provided as the fifth output of the pipeline.')
    
    
    df_steady_state = extract_df_stst_by_tspans(df_simplified_steady_state, st_span_start_t, st_span_end_t)
    df_steady_state_filtered = df_noise_cancelation(df_steady_state, method='convolution')
    df_steady_state_filtered = extract_df_stst_by_tspans(df_steady_state_filtered, st_span_start_t, st_span_end_t)
    
    file_name = 'cleaned_data_' + data_date
    sheet_name1 = 'steady state'
    sheet_name2 = 'steady state - filtered'
    save_df_excel(df_steady_state, file_name, sheet_name1, date=None)
    save_df_excel(df_steady_state_filtered, file_name, sheet_name2, date=None)
    
    
    
    out = exp_data_plotter(df_simplified_steady_state, 't [sec]', y_label= ['P_ref [kW]'], no_x_points = 20)

    return dfs_dict, dfs_dict_common, dfs_common_same_frequency, df_simplified_steady_state_avg, df_simplified_steady_state_short, df_steady_state, df_steady_state_filtered, st_span_start_t, st_span_end_t
    
    


# In[ ]:


def extract_df_stst_by_tspans(df, st_span_start_t, st_span_end_t):
    df_temp = df.copy()
    for time_span_no in range(len(st_span_start_t)):
        t1 = st_span_start_t[time_span_no]
        t2 = st_span_end_t[time_span_no]
        if time_span_no == 0:
            df_steady_state = df_time_span_provider(df_temp, time_span=[t1, t2])
        else:
            df_steady_state_current = df_time_span_provider(df_temp, time_span=[t1, t2])
            df_steady_state = pd.concat([df_steady_state, df_steady_state_current])

    
    df_steady_state = df_steady_state.reset_index(drop=True)
    
    return df_steady_state


# In[1]:


def summary(df):
    df_temp = df.copy()
    reference_column = 'P_ref [kW]'
    use_filter_data = False
    df_temp, df_temp_st, ts = steady_state_data_extractor(df_temp, ref_col=reference_column, filter_data=use_filter_data)
    df_temp_simplified_steady_state = simplified_steady_state(df_temp, filtered_data=use_filter_data)
    tol_var = 10
    df_temp_simplified_steady_state = modify_simplified_steady_state(df_temp_simplified_steady_state, tol_var, filtered_data=use_filter_data)
    df_simplified_steady_state_avg, df_simplified_steady_state_short,  st_span_start_t, st_span_end_t = dataframe_summary_provider(df_temp_simplified_steady_state, sensor_file)
    
    
    out = exp_data_plotter(df_temp_simplified_steady_state, 't [sec]', y_label= ['P_ref [kW]'], no_x_points = 20)

    
    return df_simplified_steady_state_avg, df_simplified_steady_state_short,  st_span_start_t, st_span_end_t
    
    


# In[ ]:


def reset_df(df):
    df_temp = df.copy()
    
    df_temp['t [sec]'] = df_temp['t [sec]'] - df_temp['t [sec]'].loc[0]
    df_temp.reset_index(drop=True, inplace=True)

    
    return df_temp
    


# In[ ]:


def df_time_span_selector(df, time_spans, time_col_name=None, reset_index=None):
    if reset_index is None:
        reset_index = True
        
    if time_col_name is None:
        time_col_name = 't [sec]'
    
    
    df_temp = df.copy()
    
    no_time_spans = len(time_spans)
    selected_df = pd.DataFrame([], columns=df_temp.columns)
    
    for time_span_no in range(no_time_spans):
        df = df_temp[(df_temp['t [sec]'] >= time_spans[time_span_no][0]) & (df_temp['t [sec]'] <= time_spans[time_span_no][1])]
        selected_df = selected_df.append(df)
        del df
    if reset_index:
        selected_df.reset_index(drop=True, inplace=True)
        
        
        
    return selected_df


# In[ ]:


def df_noise_cancelation_for_time_spans(df, time_spans, y_label=None, method=None, time_col_name=None, reset_index=None):
    if reset_index is None:
        reset_index = True
        
    if time_col_name is None:
        time_col_name = 't [sec]'    
        
    df_temp = df.copy()
    
    
    no_time_spans = len(time_spans)
    selected_df = pd.DataFrame([], columns=df_temp.columns)
    
    for time_span_no in range(no_time_spans):
        df = df_temp[(df_temp['t [sec]'] >= time_spans[time_span_no][0]) & (df_temp['t [sec]'] <= time_spans[time_span_no][1])]
        df = df_noise_cancelation(df, y_label=y_label, method=method)
        selected_df = selected_df.append(df)
        
        del df
    if reset_index:
        selected_df.reset_index(drop=True, inplace=True)   
        
    return selected_df
    
    


# In[3]:


def find_st_st_time_spans(df, ref_dict,time_col = 't [sec]'):
    min_delta_t = 30 # minimum duration to call a time-span "steady state"
    
    st_st_rows_list_complete = list()

    references = ref_dict.keys() 
    ref_no = 0
    
    for ref in references:
        
        tols = ref_dict[ref]
        tol = tols[0]
        dev_tol = tols[1]
        ref_row = 0
        ref_value = df[ref].iloc[ref_row]            
        variation = 0
        row_no = 0
        st_st_rows = list()
        st_st_times_spans = list()
        while ref_row < len(df) and row_no < len(df)-1:
            for row_no in range(ref_row, len(df)):
                variation = abs(df[ref].iloc[row_no]-ref_value)
                if variation > tol:
                    if df[time_col].iloc[row_no] - df[time_col].iloc[ref_row] > 1.5 * min_delta_t:       
                        st_st_ref_col = df[ref].iloc[ref_row:row_no-1]
                        st_st_t_col = df['t [sec]'].iloc[ref_row:row_no-1]
                        mean_val = st_st_ref_col.mean()
                        if mean_val > 5:
                            st_st_start = ref_row
                            st_st_end = row_no-1
                            st_st_tsp = [st_st_start, st_st_end]
                            deviation = st_st_ref_col - mean_val
                            
                            
                            for st_row_no in range(st_st_start,st_st_end):
                                rel_deviatoion = abs(deviation[st_row_no])/tol
                                if rel_deviatoion > dev_tol:
                                    st_st_end = st_row_no - 1
                                    st_st_tsp = [st_st_start, st_st_end]
                                    break
                            if df[time_col].iloc[st_st_tsp[1]] - df[time_col].iloc[st_st_tsp[0]] > min_delta_t:
                                st_st_rows.append(st_st_tsp)
                                st_st_times_spans.append([df[time_col].iloc[st_st_tsp[0]],df[time_col].iloc[st_st_tsp[1]]])
                        ref_row = row_no
                        ref_value = df[ref].iloc[ref_row]
                        break
                    else:
                        ref_row = row_no
                        ref_value = df[ref].iloc[ref_row]
                        break
    

        
        st_st_rows_list = list()
        for row_span in st_st_rows:
            st_st_rows_list.append(list(range(int(row_span[0]),int(row_span[1]))))
            
        st_st_rows_list_complete.append(flatten(st_st_rows_list))
            
        ref_no = ref_no + 1
        
    
    if len(ref_dict) > 1:
        common_st_st_rows = st_st_rows_list_complete[0]
        for ref_no in range(1, len(ref_dict)):
            common_st_st_rows = [x for x in common_st_st_rows if x in st_st_rows_list_complete[ref_no]]
        # changing complete row list to row spans:
        st_st_rows = list()
        st_st_times_spans = list()
        for counter in range(len(common_st_st_rows)):
            row_no = common_st_st_rows[counter]
            
            if counter == 0:
                start = int(row_no)
            else:
                if row_no - common_st_st_rows[counter-1] > 1:
                    end = int(common_st_st_rows[counter-1])
                    st_st_rows.append([start, end])
                    st_st_times_spans.append([df[time_col].iloc[start], df[time_col].iloc[end]])
                    start = int(row_no)
                    del end
                elif counter == len(common_st_st_rows)-1: # last point
                    end = int(common_st_st_rows[counter])
                    st_st_rows.append([start, end])
                    st_st_times_spans.append([df[time_col].iloc[start], df[time_col].iloc[end]])
    else:
        
        pass
    
    # last check on time difference in each time span 
    if len(st_st_rows) > 0:
    
        removing_rows = list()
        removing_times = list()
        for time_span_no in range(len(st_st_rows)):
            rows = st_st_rows[time_span_no]
            times = st_st_times_spans[time_span_no]
            if times[1]-times[0] < min_delta_t:
                removing_rows.append(rows)
                removing_times.append(times)
        st_st_rows = [s for s in st_st_rows if s not in removing_rows]
        st_st_times_spans = [s for s in st_st_times_spans if s not in removing_times]

        
    return st_st_rows, st_st_times_spans
            
 


# In[ ]:


def flatten(a_list):
    new_array = np.array([])
    for i in range(len(a_list)):
        new_array = np.append(new_array, a_list[i])
    return new_array

