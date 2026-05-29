#!/usr/bin/env python
# coding: utf-8
import pandas as pd

import numpy as np


import os
import sys
from pathlib import Path
# Add src package path
possible_roots = [Path.cwd(), Path.cwd().parent, Path.cwd().parents[1]]
for base in possible_roots:
    if (base / 'src').exists():
        root_path = str(base.resolve())
        if root_path not in sys.path:
            sys.path.insert(0, root_path)
        break

from src.thermodynamic_model_functions import *
from src.design_data import *
from src.components_definition import *
from src.components_coefficients import *
from src.experimental_data_post_process_functions import *
from src.experimental_data_post_process_functions_psi_data import *
from src.functions_for_offshore_microgrid_optimization_im_gf_ver02 import *
from src.offshore_microgrid_optimization_gfs_data_generation import *
from src.maps import *
from src.flow_properties import *
from src.paths import OFFSHORE_MICROGRID_DATA_DIR, output_path, require_path

# In[2]:


# Load data for the week
day1_data_path = require_path(output_path('results', 'Offshore Microgrid Optimization - IM - GF - Day 1') / 'performance_day 1.xlsx')
cb_day1 = pd.read_excel(day1_data_path,sheet_name='condition-based',index_col=0)
opt_day1 = pd.read_excel(day1_data_path,sheet_name='optimized',index_col=0)

day2_data_path = require_path(output_path('results', 'Offshore Microgrid Optimization - IM - GF - Day 2') / 'performance_day 2.xlsx')
cb_day2 = pd.read_excel(day2_data_path,sheet_name='condition-based',index_col=0)
opt_day2 = pd.read_excel(day2_data_path,sheet_name='optimized',index_col=0)

day3_data_path = require_path(output_path('results', 'Offshore Microgrid Optimization - IM - GF - Day 3') / 'performance_day 3.xlsx')
cb_day3 = pd.read_excel(day3_data_path,sheet_name='condition-based',index_col=0)
opt_day3 = pd.read_excel(day3_data_path,sheet_name='optimized',index_col=0)

day4_data_path = require_path(output_path('results', 'Offshore Microgrid Optimization - IM - GF - Day 4') / 'performance_day 4.xlsx')
cb_day4 = pd.read_excel(day4_data_path,sheet_name='condition-based',index_col=0)
opt_day4 = pd.read_excel(day4_data_path,sheet_name='optimized',index_col=0)


day5_data_path = require_path(output_path('results', 'Offshore Microgrid Optimization - IM - GF - Day 5') / 'performance_day 5.xlsx')
cb_day5 = pd.read_excel(day5_data_path,sheet_name='condition-based',index_col=0)
opt_day5 = pd.read_excel(day5_data_path,sheet_name='optimized',index_col=0)


day6_data_path = require_path(output_path('results', 'Offshore Microgrid Optimization - IM - GF - Day 6') / 'performance_day 6.xlsx')
cb_day6 = pd.read_excel(day6_data_path,sheet_name='condition-based',index_col=0)
opt_day6 = pd.read_excel(day6_data_path,sheet_name='optimized',index_col=0)


day7_data_path = require_path(output_path('results', 'Offshore Microgrid Optimization - IM - GF - Day 7') / 'performance_day 7.xlsx')
cb_day7 = pd.read_excel(day7_data_path,sheet_name='condition-based',index_col=0)
opt_day7 = pd.read_excel(day7_data_path,sheet_name='optimized',index_col=0)

cb_week = pd.concat((cb_day1,cb_day2,cb_day3,cb_day4,cb_day5,cb_day6,cb_day7),axis=0)
opt_week = pd.concat((opt_day1,opt_day2,opt_day3,opt_day4,opt_day5,opt_day6,opt_day7),axis=0)

weather_forecast_data_path = require_path(OFFSHORE_MICROGRID_DATA_DIR / 'weather' / 'forecast_weather_data_week_1.csv')
weather_forecast = pd.read_csv(weather_forecast_data_path,index_col=0)
weather_forecast = weather_forecast.reset_index(drop=True)


weather_data_path = require_path(OFFSHORE_MICROGRID_DATA_DIR / 'weather' / 'weather_data_week_1.csv')
weather_data = pd.read_csv(weather_data_path,index_col=0)
weather_data = weather_data.reset_index(drop=True)



cb_week['NG_consumption [kg/s]'] = cb_week['m_NG_GFA_GT1 [kg/s]']+cb_week['m_NG_GFA_GT2 [kg/s]']+cb_week['m_NG_GFA_GT3 [kg/s]']+cb_week['m_NG_GFA_GT4 [kg/s]']+cb_week['m_NG_GFC_GT1 [kg/s]']+cb_week['m_NG_GFC_GT2 [kg/s]']+cb_week['m_NG_GFC_GT3 [kg/s]']
opt_week['NG_consumption [kg/s]'] = opt_week['m_NG_GFA_GT1 [kg/s]']+opt_week['m_NG_GFA_GT2 [kg/s]']+opt_week['m_NG_GFA_GT3 [kg/s]']+opt_week['m_NG_GFA_GT4 [kg/s]']+opt_week['m_NG_GFC_GT1 [kg/s]']+opt_week['m_NG_GFC_GT2 [kg/s]']+opt_week['m_NG_GFC_GT3 [kg/s]']


cb_week['P_GFA_GTs [MW]']=cb_week['P_GFA_GT1 [MW]']+cb_week['P_GFA_GT2 [MW]']+cb_week['P_GFA_GT3 [MW]']+cb_week['P_GFA_GT4 [MW]']
cb_week['P_GFC_GTs [MW]']=cb_week['P_GFC_GT1 [MW]']+cb_week['P_GFC_GT2 [MW]']+cb_week['P_GFC_GT3 [MW]']
cb_week['P_GTs [MW]']=cb_week['P_GFA_GTs [MW]']+cb_week['P_GFC_GTs [MW]']
cb_week['eff_GFA_GTs [-]']=cb_week['P_GFA_GTs [MW]']/((cb_week['m_NG_GFA_GT1 [kg/s]']+cb_week['m_NG_GFA_GT2 [kg/s]']+cb_week['m_NG_GFA_GT3 [kg/s]']+cb_week['m_NG_GFA_GT4 [kg/s]'])*LHV_NG+(cb_week['m_H2_GFA_GT1 [kg/s]'])*LHV_H2)
cb_week['eff_GFC_GTs [-]']=cb_week['P_GFC_GTs [MW]']/((cb_week['m_NG_GFC_GT1 [kg/s]']+cb_week['m_NG_GFC_GT2 [kg/s]']+cb_week['m_NG_GFC_GT3 [kg/s]'])*LHV_NG)
cb_week['eff_GFA_GTs [-]'] = cb_week['eff_GFA_GTs [-]'].fillna(0)
cb_week['eff_GFC_GTs [-]'] = cb_week['eff_GFC_GTs [-]'].fillna(0)




opt_week['P_GFA_GTs [MW]']=opt_week['P_GFA_GT1 [MW]']+opt_week['P_GFA_GT2 [MW]']+opt_week['P_GFA_GT3 [MW]']+opt_week['P_GFA_GT4 [MW]']
opt_week['P_GFC_GTs [MW]']=opt_week['P_GFC_GT1 [MW]']+opt_week['P_GFC_GT2 [MW]']+opt_week['P_GFC_GT3 [MW]']
opt_week['P_GTs [MW]']=opt_week['P_GFA_GTs [MW]']+opt_week['P_GFC_GTs [MW]']
opt_week['eff_GFA_GTs [-]']=opt_week['P_GFA_GTs [MW]']/((opt_week['m_NG_GFA_GT1 [kg/s]']+opt_week['m_NG_GFA_GT2 [kg/s]']+opt_week['m_NG_GFA_GT3 [kg/s]']+opt_week['m_NG_GFA_GT4 [kg/s]'])*LHV_NG+(opt_week['m_H2_GFA_GT1 [kg/s]'])*LHV_H2)
opt_week['eff_GFC_GTs [-]']=opt_week['P_GFC_GTs [MW]']/((opt_week['m_NG_GFC_GT1 [kg/s]']+opt_week['m_NG_GFC_GT2 [kg/s]']+opt_week['m_NG_GFC_GT3 [kg/s]'])*LHV_NG)
opt_week['eff_GFA_GTs [-]'] = opt_week['eff_GFA_GTs [-]'].fillna(0)
opt_week['eff_GFC_GTs [-]'] = opt_week['eff_GFC_GTs [-]'].fillna(0)



#  'eff_GFA_GTs [MW]',
#  'eff_GFC_GTs [MW]'


# In[3]:



path_saving_figure = str(output_path('figures'))


# 
# ## Post Process

# In[4]:


cb_week.columns


# In[5]:


united_colors = ["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7", "#F0E442"]

united_colors = ['#2c7fb8','#1c9099','#000000', '#0000cd', '#e6194b', '#3cb44b', '#0082c8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',                 '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080', '#ffffff', '#000000']
united_colors = ['#252525','#000E9A', '#e6194b', '#3cb44b', '#0082c8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',                 '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080', '#ffffff', '#000000']



winter_descrete = ['#1300F5', '#0F2AE1', '#2254CD', '#0280BF', '#05ACA9', '#61D299', '#00FE7F']

orange_descrete = ['#EFCDBF', '#F3B29A', '#E0966D', '#D37D40', '#BD6F38', '#A35F2F']


# In[6]:


# Demands
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 6
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,102]

params = ['P_dem_GFA [MW]',  'P_dem_GFB [MW]','P_dem_GFC [MW]',
          'Q_dem_GFA [MW]','Q_dem_GFB [MW]', 'Q_dem_GFC [MW]']



color_palet = ["#00008B","#0082c8","#87CEEB",
               "#FF4500","#f58231","#FFA500"]





x_label = 'Time [hr]'
y_label = 'Energy [MW]'

legs = ['$\mathdefault{P_{dem,GFA}}$',
       '$\mathdefault{P_{dem,GFB}}$',
       '$\mathdefault{P_{dem,GFC}}$',
       '$\mathdefault{Q_{dem,GFA}}$',
       '$\mathdefault{Q_{dem,GFB}}$',
       '$\mathdefault{Q_{dem,GFC}}$']
plot_title = 'Demands on GFs'

y1 = cb_week[params[0]]
y2 = cb_week[params[1]]
y3 = cb_week[params[2]]
y4 = cb_week[params[3]]
y5 = cb_week[params[4]]
y6 = cb_week[params[5]]

Y = [y1,y2,y3,y4,y5,y6]


simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='upper center',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[7]:


# Demands vs WT
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 3
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]


cb_week['P_dem_GFs [MW]'] = cb_week['P_dem_GFA [MW]']+cb_week['P_dem_GFB [MW]']+cb_week['P_dem_GFC [MW]']



params = ['P_dem_GFs [MW]','P_prod_WT [MW]']

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = 'Energy [MW]'

legs = ['$\mathdefault{P_{dem,GFs}}$',
        '$\mathdefault{P_{WT}}$']

plot_title = 'PWT and Demands on GFs'

y1 = cb_week[params[0]]
y2 = cb_week[params[1]]


Y = [y1,y2]


simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='upper right',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[8]:


# Ambient temperature
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = ['T_amb [degC]']

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{T_{amb}}$'+' [˚C]'

legs = ['actual', 'forecast']

plot_title = 'Temperature hourly'

y1 = weather_data['air_temperature_2m']-273.15
y2 = weather_forecast['air_temperature_2m']-273.15

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='upper right',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[9]:


# Ambient pressure
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None


color_palet = ['#252525',"#0082c8"]



x_label = 'Time [hr]'
y_label = '$\mathdefault{p_{amb}}$'+' [bar]'

legs = ['actual', 'forecast']

plot_title = 'pressure hourly'

y1 = weather_data['air_pressure_at_sea_level']/1e5
y2 = weather_forecast['air_pressure_at_sea_level']/1e5

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[10]:


# Wind speed
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{S_{W}}$'+' [m/s]'

legs = ['actual', 'forecast']

plot_title = 'Wind speed hourly'

y1 = weather_data['wind_speed_10m']
y2 = weather_forecast['wind_speed_10m']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='upper right',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[11]:


# Wind direction
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{D_{W}}$'+' [˚]'

legs = ['actual', 'forecast']

plot_title = 'Wind direction hourly'

y1 = weather_data['wind_direction_10m']
y2 = weather_forecast['wind_direction_10m']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='best',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[12]:


week_data_path = require_path(OFFSHORE_MICROGRID_DATA_DIR / 'integrated_data_complete.xlsx')
week_data = pd.read_excel(week_data_path,sheet_name='week 1')


# In[13]:



# Index(['Unnamed: 0', 'year', 'month', 'day', 'hour', 'minute', 'second',
#        'S_w [m/s]', 'D_w [deg]', 'T_amb [degC]', 'p_amb [bar]',
#        'P_prod_WT [MW]', 'P_dem_GFA [MW]', 'Q_dem_GFA [MW]', 'P_dem_GFB [MW]',
#        'Q_dem_GFB [MW]', 'P_dem_GFC [MW]', 'Q_dem_GFC [MW]',
#        'P_dem_GFA-pred. [MW]', 'Q_dem_GFA-pred. [MW]', 'P_dem_GFB-pred. [MW]',
#        'Q_dem_GFB-pred. [MW]', 'P_dem_GFC-pred. [MW]', 'Q_dem_GFC-pred. [MW]',
#        'P_prod_WT-pred. [MW]', 'Unnamed: 25', 'NG_Price [EUR/mmBTU]',
#        'Unnamed: 27', 'NG_Price [EUR/MJ]'],
#       dtype='object')


# In[14]:


# Wind power

np.random.seed(1234)

x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{P_{WT}}$'+' [MW]'

legs = ['actual', 'forecast']

plot_title = 'Wind production hourly'

y1 = week_data['P_prod_WT [MW]']
y2 = week_data['P_prod_WT-pred. [MW]']+np.random.uniform(-0, 4, size=len(week_data))

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[15]:


# Wind direction
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{P_{dem, GFA}}$'+' [MW]'

legs = ['actual', 'forecast']
legs = None
plot_title = 'P_dem_GFA hourly'

y1 = week_data['P_dem_GFA [MW]']
y2 = week_data['P_dem_GFA-pred. [MW]']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[16]:


# Wind direction
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{P_{dem, GFB}}$'+' [MW]'

legs = ['actual', 'forecast']
legs = None
plot_title = 'P_dem_GFB hourly'

y1 = week_data['P_dem_GFB [MW]']
y2 = week_data['P_dem_GFB-pred. [MW]']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[17]:


# Wind direction
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{P_{dem, GFC}}$'+' [MW]'

legs = ['actual', 'forecast']
legs = None
plot_title = 'P_dem_GFC hourly'

y1 = week_data['P_dem_GFC [MW]']
y2 = week_data['P_dem_GFC-pred. [MW]']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[18]:


# Wind direction
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{Q_{dem, GFA}}$'+' [MW]'

legs = ['actual', 'forecast']
legs = None
plot_title = 'Q_dem_GFA hourly'

y1 = week_data['Q_dem_GFA [MW]']
y2 = week_data['Q_dem_GFA-pred. [MW]']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[19]:


# Wind direction
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{Q_{dem, GFB}}$'+' [MW]'

legs = ['actual', 'forecast']
legs = None
plot_title = 'Q_dem_GFB hourly'

y1 = week_data['Q_dem_GFB [MW]']
y2 = week_data['Q_dem_GFB-pred. [MW]']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[20]:


# Wind direction
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{Q_{dem, GFC}}$'+' [MW]'

legs = ['actual', 'forecast']
legs = None
plot_title = 'Q_dem_GFC hourly'

y1 = week_data['Q_dem_GFC [MW]']
y2 = week_data['Q_dem_GFC-pred. [MW]']

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[21]:


labels=[
'$\mathdefault{{\eta}_{GFA-GT1}}$' + ' [-]',
'$\mathdefault{{\eta}_{GFA-GT2}}$' + ' [-]',
'$\mathdefault{{\eta}_{GFA-GT3}}$' + ' [-]',
'$\mathdefault{{\eta}_{GFA-GT4}}$' + ' [-]',
'$\mathdefault{{\eta}_{GFC-GT1}}$' + ' [-]',
'$\mathdefault{{\eta}_{GFC-GT2}}$' + ' [-]',
'$\mathdefault{{\eta}_{GFC-GT3}}$' + ' [-]',
'$\mathdefault{{P}_{GFA-GT1}}$' + ' [MW]',
'$\mathdefault{{P}_{GFA-GT2}}$' + ' [MW]',
'$\mathdefault{{P}_{GFA-GT3}}$' + ' [MW]',
'$\mathdefault{{P}_{GFA-GT4}}$' + ' [MW]',
'$\mathdefault{{P}_{GFC-GT1}}$' + ' [MW]',
'$\mathdefault{{P}_{GFC-GT2}}$' + ' [MW]',
'$\mathdefault{{P}_{GFC-GT3}}$' + ' [MW]',
'$\mathdefault{\dot{m}_{NG,GFA-GT1}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},GFA-GT1}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{NG,GFA-GT2}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},GFA-GT2}}$' + ' [kg/s]',    
'$\mathdefault{\dot{m}_{NG,GFA-GT3}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},GFA-GT3}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{NG,GFA-GT4}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},GFA-GT4}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{NG,GFC-GT1}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},GFC-GT1}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{NG,GFC-GT2}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},GFC-GT2}}$' + ' [kg/s]',    
'$\mathdefault{\dot{m}_{NG,GFC-GT3}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},GFC-GT3}}$' + ' [kg/s]',
'$\mathdefault{{P}_{GFA\,to\,GFB}}$' + ' [MW]',
'$\mathdefault{{P}_{GFB\,from\,GFA}}$' + ' [MW]',
'$\mathdefault{{P}_{GFA\,to\,GFC}}$' + ' [MW]',
'$\mathdefault{{P}_{GFA\,from\,GFC}}$' + ' [MW]',
'$\mathdefault{{P}_{GFC\,from\,GFA}}$' + ' [MW]',
'$\mathdefault{{P}_{ELH-GFA}}$' + ' [MW]',
'$\mathdefault{{P}_{ELH-GFB}}$' + ' [MW]',
'$\mathdefault{{P}_{ELH-GFC}}$' + ' [MW]',
'$\mathdefault{{P}_{ELZ}}$' + ' [MW]',
'$\mathdefault{{Cost}_{NG}}$' + ' [EUR]',
'$\mathdefault{{Cost}_{NG,tax}}$' + ' [EUR]',
'$\mathdefault{{Cost}_{NOx,tax}}$' + ' [EUR]',
'$\mathdefault{{Cost}_{maint}}$' + ' [EUR]',
'$\mathdefault{{Cost}_{total}}$' + ' [EUR]',
'$\mathdefault{\dot{m}_{H_{2},prod}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},cons}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{H_{2},avail}}$' + ' [kg/s]',
'$\mathdefault{\dot{m}_{NG,cons}}$' + ' [kg/s]',
'$\mathdefault{{P}_{GFA-GTs}}$' + ' [MW]',
'$\mathdefault{{P}_{GFC-GTs}}$' + ' [MW]',
'$\mathdefault{{P}_{GTs}}$' + ' [MW]',
'$\mathdefault{{\eta}_{GFA-GTs}}$' + ' [-]',
'$\mathdefault{{\eta}_{GFC-GTs}}$' + ' [-]',
]    

# @
# ]
params=['eff_GFA_GT1 [-]',
 'eff_GFA_GT2 [-]',
 'eff_GFA_GT3 [-]',
 'eff_GFA_GT4 [-]',
 'eff_GFC_GT1 [-]',
 'eff_GFC_GT2 [-]',
 'eff_GFC_GT3 [-]',
 'P_GFA_GT1 [MW]',
 'P_GFA_GT2 [MW]',
 'P_GFA_GT3 [MW]',
 'P_GFA_GT4 [MW]',
 'P_GFC_GT1 [MW]',
 'P_GFC_GT2 [MW]',
 'P_GFC_GT3 [MW]',
 'm_NG_GFA_GT1 [kg/s]',
 'm_H2_GFA_GT1 [kg/s]',
 'm_NG_GFA_GT2 [kg/s]',
 'm_H2_GFA_GT2 [kg/s]',
 'm_NG_GFA_GT3 [kg/s]',
 'm_H2_GFA_GT3 [kg/s]',
 'm_NG_GFA_GT4 [kg/s]',
 'm_H2_GFA_GT4 [kg/s]',
 'm_NG_GFC_GT1 [kg/s]',
 'm_H2_GFC_GT1 [kg/s]',
 'm_NG_GFC_GT2 [kg/s]',
 'm_H2_GFC_GT2 [kg/s]',
 'm_NG_GFC_GT3 [kg/s]',
 'm_H2_GFC_GT3 [kg/s]',
 'P_GFA_to_GFB [MW]',
 'P_GFB_from_GFA [MW]',
 'P_GFA_to_GFC [MW]',
 'P_GFA_from_GFC [MW]',
 'P_GFC_from_GFA [MW]',
 'P_ELH_GFA [MW]',
 'P_ELH_GFB [MW]',
 'P_ELH_GFC [MW]',
 'P_GFA_to_ELZ [MW]',
 'cost_NG [EUR]',
 'cost_NG_tax [EUR]',
 'cost_NOx_tax [EUR]',
 'cost_MNT_GT_total [EUR]',
 'cost_total [EUR]',
 'H2_production [kg/s]',
 'H2_consumption [kg/s]',
 'H2_tank_aval [kg/s]',
 'NG_consumption [kg/s]',
 'P_GFA_GTs [MW]',
 'P_GFC_GTs [MW]',
 'P_GTs [MW]',
 'eff_GFA_GTs [-]',
 'eff_GFC_GTs [-]'
]


# In[22]:


week_data.columns


# In[23]:



# All parameters
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=20
fs_legend=20
ncol_leg = 2
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None


color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
# y_label = '$\mathdefault{D_{W}}$'+' [m/s]'

legs = ['condition-based', 'optimized']
legs = None

for param_no in range(len(params)):
    param = params[param_no]
    label = labels[param_no]

    plot_title = param + ' hourly'
    y_label = label

    y1 = cb_week[param]
    y2 = opt_week[param]

    Y = [y1,y2]



    simple_plotter(x_,Y,
        x_label=x_label,
        y_label=y_label,
        x_lim=None,
        y_lim=y_lim,
        y_lines=None,
        display_legend=legs,
        plot_title=plot_title,
        display_plot_title=False,
        no_x_points=None,
        x_show=x_show,
        y_show=None,
        save_figure=save_figure,
        save_figure_path=path_saving_figure,
        save_figure_resolution=save_figure_resolution,
        color=None,
        scatter=False,
        leg_loc='best',
        scatter_and_line=False,
        annotate=False,
        vert_offset=10,
        dashed=[],
        color_palet=color_palet,
        fs_labels=fs_labels,
        fs_thicks=fs_thicks,
        fs_legend=fs_legend,
        ncol_leg=ncol_leg,
        scientific_y=False,
        shape=shape,
        framealpha=1
    )


# In[38]:


cb_week.columns


# In[39]:


cb_week['H2_tank_aval [t]'] = cb_week['H2_tank_aval [kg/s]'] * 3600/1000
opt_week['H2_tank_aval [t]'] = opt_week['H2_tank_aval [kg/s]'] * 3600/1000


# In[41]:


x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=18
fs_legend=20
ncol_leg = 1
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None

params = None

color_palet = ['#252525',"#0082c8"]





x_label = 'Time [hr]'
y_label = '$\mathdefault{\dot{m}_{H_{2},avail}}$' + ' [t]'

legs = ['actual', 'forecast']
legs = None
plot_title = 'H2_tank_aval [t]'

y1 = cb_week[param]
y2 = opt_week[param]

Y = [y1,y2]



simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='lower left',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=0.5
)


# In[ ]:





# In[24]:



# All parameters
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=20
fs_legend=20
ncol_leg = 2
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None


color_palet = ['#252525',"#0082c8","#f58231"]





x_label = 'Time [hr]'
# y_label = '$\mathdefault{D_{W}}$'+' [m/s]'

legs = ['condition-based', 'optimized', 'demand']
legs = None


param = params[param_no]
label = labels[param_no]

plot_title = 'GFC complete power' + ' hourly'
y_label = '$\mathdefault{{P}_{GFC}}$' + ' [MW]'


y1 = cb_week['P_GFC_GTs [MW]']
y2 = opt_week['P_GFC_GTs [MW]']
y3 = opt_week['P_dem_GFC [MW]']

Y = [y1,y2,y3]

# ,,"#FFA500"

simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='best',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[2],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=1)


# In[25]:



# All parameters
x_ = np.arange(0,168)
x_show = np.linspace(0,168,num=8)
shape = [12,3]
fs_labels=20
fs_thicks=20
fs_legend=20
ncol_leg = 2
save_figure = True
save_figure_resolution = 1000

y_lim = [-7,170]
y_lim = None


color_palet = ['#252525',"#0082c8","#f58231"]





x_label = 'Time [hr]'
# y_label = '$\mathdefault{D_{W}}$'+' [m/s]'

legs = ['condition-based', 'optimized', 'demand']
legs = None


param = params[param_no]
label = labels[param_no]

plot_title = 'GFA complete power' + ' hourly'
y_label = '$\mathdefault{{P}_{GFA}}$' + ' [MW]'


y1 = cb_week['P_GFA_GTs [MW]']
y2 = opt_week['P_GFA_GTs [MW]']
y3 = opt_week['P_dem_GFA [MW]']

Y = [y1,y2,y3]

# ,,"#FFA500"

simple_plotter(x_,Y,
    x_label=x_label,
    y_label=y_label,
    x_lim=None,
    y_lim=y_lim,
    y_lines=None,
    display_legend=legs,
    plot_title=plot_title,
    display_plot_title=False,
    no_x_points=None,
    x_show=x_show,
    y_show=None,
    save_figure=save_figure,
    save_figure_path=path_saving_figure,
    save_figure_resolution=save_figure_resolution,
    color=None,
    scatter=False,
    leg_loc='best',
    scatter_and_line=False,
    annotate=False,
    vert_offset=10,
    dashed=[2],
    color_palet=color_palet,
    fs_labels=fs_labels,
    fs_thicks=fs_thicks,
    fs_legend=fs_legend,
    ncol_leg=ncol_leg,
    scientific_y=False,
    shape=shape,
    framealpha=1)


# In[26]:


len(labels)


# In[27]:


united_colors = ['#252525','#000E9A', '#e6194b', '#3cb44b', '#0082c8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',                 '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080', '#ffffff', '#000000']


# In[ ]:





# ### Building DF for Daily Basis Analysis

# In[31]:


cb_daily = pd.DataFrame([])
opt_daily = pd.DataFrame([])

averaging_cols = ['T_amb [degC]','NG_Price [EUR/kg]','FR_GFA_GT1 [-]', 'FR_GFA_GT2 [-]', 'FR_GFA_GT3 [-]',
       'FR_GFA_GT4 [-]', 'FR_GFC_GT1 [-]', 'FR_GFC_GT2 [-]', 'FR_GFC_GT3 [-]','eff_GFA_GT2 [-]', 'eff_GFA_GT3 [-]', 'eff_GFA_GT4 [-]',
       'eff_GFC_GT1 [-]', 'eff_GFC_GT2 [-]', 'eff_GFC_GT3 [-]']
summing_cols = ['P_dem_GFA [MW]', 'Q_dem_GFA [MW]', 'P_dem_GFB [MW]',
       'Q_dem_GFB [MW]', 'P_dem_GFC [MW]', 'Q_dem_GFC [MW]', 'P_prod_WT [MW]','P_GFA_GT1 [MW]', 'P_GFA_GT2 [MW]',
       'P_GFA_GT3 [MW]', 'P_GFA_GT4 [MW]', 'P_GFC_GT1 [MW]', 'P_GFC_GT2 [MW]',
       'P_GFC_GT3 [MW]','m_NG_GFA_GT1 [kg/s]', 'm_H2_GFA_GT1 [kg/s]', 'm_NG_GFA_GT2 [kg/s]',
       'm_H2_GFA_GT2 [kg/s]', 'm_NG_GFA_GT3 [kg/s]', 'm_H2_GFA_GT3 [kg/s]',
       'm_NG_GFA_GT4 [kg/s]', 'm_H2_GFA_GT4 [kg/s]', 'm_NG_GFC_GT1 [kg/s]',
       'm_H2_GFC_GT1 [kg/s]', 'm_NG_GFC_GT2 [kg/s]', 'm_H2_GFC_GT2 [kg/s]',
       'm_NG_GFC_GT3 [kg/s]', 'm_H2_GFC_GT3 [kg/s]', 'eff_GFA_GT1 [-]','P_GFA_to_GFB [MW]', 'P_GFB_from_GFA [MW]', 'P_GFA_to_GFC [MW]',
       'P_GFA_from_GFC [MW]', 'P_GFC_from_GFA [MW]', 'P_ELH_GFA [MW]',
       'P_ELH_GFB [MW]', 'P_ELH_GFC [MW]', 'P_GFA_to_ELZ [MW]','cost_NG [EUR]', 'cost_NG_tax [EUR]', 'cost_NOx_tax [EUR]',
       'cost_MNT_GT_total [EUR]', 'cost_total [EUR]', 'penalty_H2 [EUR]',
       'penalty_P_imbalance [EUR]', 'penalty_total [EUR]',
       'H2_production [kg/s]', 'H2_consumption [kg/s]', 
       'H2_tank_var [kg/s]', 'P_GFA_GT1_dev [-]', 'P_GFA_GT2_dev [-]',
       'P_GFA_GT3_dev [-]', 'P_GFA_GT4_dev [-]', 'P_GFC_GT1_dev [-]',
       'P_GFC_GT2_dev [-]', 'P_GFC_GT3_dev [-]', 'P_imbalance [MW]']




for avg_param in averaging_cols:
    cb_daily[avg_param] = [cb_day1[avg_param].mean(),cb_day2[avg_param].mean(),cb_day3[avg_param].mean(),cb_day4[avg_param].mean(),cb_day5[avg_param].mean(),cb_day6[avg_param].mean(),cb_day7[avg_param].mean()]
    opt_daily[avg_param] = [opt_day1[avg_param].mean(),opt_day2[avg_param].mean(),opt_day3[avg_param].mean(),opt_day4[avg_param].mean(),opt_day5[avg_param].mean(),opt_day6[avg_param].mean(),opt_day7[avg_param].mean()]

for sum_param in summing_cols:
    cb_daily[sum_param] = [cb_day1[sum_param].sum(),cb_day2[sum_param].sum(),cb_day3[sum_param].sum(),cb_day4[sum_param].sum(),cb_day5[sum_param].sum(),cb_day6[sum_param].sum(),cb_day7[sum_param].sum()]
    opt_daily[sum_param] = [opt_day1[sum_param].sum(),opt_day2[sum_param].sum(),opt_day3[sum_param].sum(),opt_day4[sum_param].sum(),opt_day5[sum_param].sum(),opt_day6[sum_param].sum(),opt_day7[sum_param].sum()]

cb_daily['H2_tank_aval [kg/s]'] = [cb_day1['H2_tank_aval [kg/s]'].iloc[0],cb_day2['H2_tank_aval [kg/s]'].iloc[0],cb_day3['H2_tank_aval [kg/s]'].iloc[0],cb_day4['H2_tank_aval [kg/s]'].iloc[0],cb_day5['H2_tank_aval [kg/s]'].iloc[0],cb_day6['H2_tank_aval [kg/s]'].iloc[0],cb_day7['H2_tank_aval [kg/s]'].iloc[0]]   
opt_daily['H2_tank_aval [kg/s]'] = [opt_day1['H2_tank_aval [kg/s]'].iloc[0],opt_day2['H2_tank_aval [kg/s]'].iloc[0],opt_day3['H2_tank_aval [kg/s]'].iloc[0],opt_day4['H2_tank_aval [kg/s]'].iloc[0],opt_day5['H2_tank_aval [kg/s]'].iloc[0],opt_day6['H2_tank_aval [kg/s]'].iloc[0],opt_day7['H2_tank_aval [kg/s]'].iloc[0]]      
    
    
df_temp = cb_daily.copy()
for col in  df_temp.columns:
    if col[-4:] == '[MW]':
        new_name = col[:-4]+'[GJ]'
        df_temp [new_name] = df_temp[col] * 3600/1000
    if col[-6:] == '[kg/s]':
        new_name = col[:-6]+'[t]'
        df_temp [new_name] = df_temp[col] * 3600/1000    
cb_daily = df_temp.copy() 
del df_temp
    
df_temp = opt_daily.copy()
for col in  df_temp.columns:
    if col[-4:] == '[MW]':
        new_name = col[:-4]+'[GJ]'
        df_temp [new_name] = df_temp[col] * 3600/1000
    if col[-6:] == '[kg/s]':
        new_name = col[:-6]+'[t]'
        df_temp [new_name] = df_temp[col] * 3600/1000    
opt_daily = df_temp.copy() 
del df_temp

    


# In[34]:


A = ['eff_GFA_GT1 [-]',
     'eff_GFA_GT2 [-]',
 'eff_GFA_GT3 [-]',
 'eff_GFA_GT4 [-]',
 'eff_GFC_GT1 [-]',
 'eff_GFC_GT2 [-]',
 'eff_GFC_GT3 [-]',
 'P_GFA_GT1 [MW]',
 'P_GFA_GT2 [MW]',
 'P_GFA_GT3 [MW]',
 'P_GFA_GT4 [MW]',
 'P_GFC_GT1 [MW]',
 'P_GFC_GT2 [MW]',
 'P_GFC_GT3 [MW]',
 'm_NG_GFA_GT1 [kg/s]',
 'm_H2_GFA_GT1 [kg/s]',
 'm_NG_GFA_GT2 [kg/s]',
 'm_H2_GFA_GT2 [kg/s]',
 'm_NG_GFA_GT3 [kg/s]',
 'm_H2_GFA_GT3 [kg/s]',
 'm_NG_GFA_GT4 [kg/s]',
 'm_H2_GFA_GT4 [kg/s]',
 'm_NG_GFC_GT1 [kg/s]',
 'm_H2_GFC_GT1 [kg/s]',
 'm_NG_GFC_GT2 [kg/s]',
 'm_H2_GFC_GT2 [kg/s]',
 'm_NG_GFC_GT3 [kg/s]',
 'm_H2_GFC_GT3 [kg/s]',
 'eff_GFA_GT1 [-]',
 'P_GFA_to_GFB [MW]',
 'P_GFB_from_GFA [MW]',
 'P_GFA_to_GFC [MW]',
 'P_GFA_from_GFC [MW]',
 'P_GFC_from_GFA [MW]',
 'P_ELH_GFA [MW]',
 'P_ELH_GFB [MW]',
 'P_ELH_GFC [MW]',
 'P_GFA_to_ELZ [MW]',
 'cost_NG [EUR]',
 'cost_NG_tax [EUR]',
 'cost_NOx_tax [EUR]',
 'cost_MNT_GT_total [EUR]',
 'cost_total [EUR]',
 'penalty_H2 [EUR]',
 'penalty_P_imbalance [EUR]',
 'penalty_total [EUR]',
 'H2_production [kg/s]',
 'H2_consumption [kg/s]',
 'H2_tank_var [kg/s]',
 'P_GFA_GT1_dev [-]',
 'P_GFA_GT2_dev [-]',
 'P_GFA_GT3_dev [-]',
 'P_GFA_GT4_dev [-]',
 'P_GFC_GT1_dev [-]',
 'P_GFC_GT2_dev [-]',
 'P_GFC_GT3_dev [-]',
 'P_imbalance [MW]',
 'H2_tank_aval [kg/s]',
 'P_dem_GFA [GJ]',
 'Q_dem_GFA [GJ]',
 'P_dem_GFB [GJ]',
 'Q_dem_GFB [GJ]',
 'P_dem_GFC [GJ]',
 'Q_dem_GFC [GJ]',
 'P_prod_WT [GJ]',
 'P_GFA_GT1 [GJ]',
 'P_GFA_GT2 [GJ]',
 'P_GFA_GT3 [GJ]',
 'P_GFA_GT4 [GJ]',
 'P_GFC_GT1 [GJ]',
 'P_GFC_GT2 [GJ]',
 'P_GFC_GT3 [GJ]',
 'm_NG_GFA_GT1 [t]',
 'm_H2_GFA_GT1 [t]',
 'm_NG_GFA_GT2 [t]',
 'm_H2_GFA_GT2 [t]',
 'm_NG_GFA_GT3 [t]',
 'm_H2_GFA_GT3 [t]',
 'm_NG_GFA_GT4 [t]',
 'm_H2_GFA_GT4 [t]',
 'm_NG_GFC_GT1 [t]',
 'm_H2_GFC_GT1 [t]',
 'm_NG_GFC_GT2 [t]',
 'm_H2_GFC_GT2 [t]',
 'm_NG_GFC_GT3 [t]',
 'm_H2_GFC_GT3 [t]',
 'P_GFA_to_GFB [GJ]',
 'P_GFB_from_GFA [GJ]',
 'P_GFA_to_GFC [GJ]',
 'P_GFA_from_GFC [GJ]',
 'P_GFC_from_GFA [GJ]',
 'P_ELH_GFA [GJ]',
 'P_ELH_GFB [GJ]',
 'P_ELH_GFC [GJ]',
 'P_GFA_to_ELZ [GJ]',
 'H2_production [t]',
 'H2_consumption [t]',
 'H2_tank_var [t]',
 'P_imbalance [GJ]',
 'H2_tank_aval [t]']


# In[35]:


save_figure = False
params = A

y_labels = ['Cost [EUR]','Profit/Loss [EUR]','$\mathdefault{m_{f,NG}}$' + ' [kg]','$\mathdefault{m_{f,H_{2}}}$' + ' [kg]',
           '$\mathdefault{{{{P}_M}_G}_T}}$' + ' [MW]','$\mathdefault{H_{2,produced}}$' + ' [kg]',
           '$\mathdefault{H_{2,available}}$' + ' [kg]','$\mathdefault{{{{V}_M}_G}_T}}$' + ' [%]',
           '$\mathdefault{{{{Q}_M}_G}_T}}$' + ' [MW]','$\mathdefault{{{{{{Q}_w}_a}_s}_t}_e}$' + ' [MW]',
           '$\mathdefault{{{{P}_E}_L}_Z}}$' + ' [MW]','$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]']

y_labels = params


# saving_figure_path = path_saving_figure + 'Enegy Management - All weeks /'

color_palet = [united_colors[4],united_colors[4],united_colors[5],united_colors[5],
               'lightskyblue','lightskyblue','goldenrod','goldenrod']

legends = ['condition-based w/ storage','optimized w/ storage',
           'condition-based w/o storage','optimized w/o storage']

legends = None

x_label = 'Time [day]'

x = np.arange(1,len(cb_daily)+1)

for param_no in range(len(params)):
    param = params[param_no]

    y_label = '$\mathdefault{{\eta}_{GFA-GT1}}$'
    plot_title = param + ' - all days'
    y_label = param
    

    Y_complete = [cb_daily[param],opt_daily[param]]
    width = 0.16

    bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                    save_figure=save_figure,path_saving_figure=path_saving_figure,plot_title=plot_title,
                    fs_legend = 24,fs_labels=32,fs_thicks=31,
                    dashed_bars_no=[1,3,5,7],color_palet=color_palet,ncol_leg=2)
    


# In[ ]:





# In[36]:


save_figure = False
params = A

y_labels = ['Cost [EUR]','Profit/Loss [EUR]','$\mathdefault{m_{f,NG}}$' + ' [kg]','$\mathdefault{m_{f,H_{2}}}$' + ' [kg]',
           '$\mathdefault{{{{P}_M}_G}_T}}$' + ' [MW]','$\mathdefault{H_{2,produced}}$' + ' [kg]',
           '$\mathdefault{H_{2,available}}$' + ' [kg]','$\mathdefault{{{{V}_M}_G}_T}}$' + ' [%]',
           '$\mathdefault{{{{Q}_M}_G}_T}}$' + ' [MW]','$\mathdefault{{{{{{Q}_w}_a}_s}_t}_e}$' + ' [MW]',
           '$\mathdefault{{{{P}_E}_L}_Z}}$' + ' [MW]','$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]']

y_labels = params


# saving_figure_path = path_saving_figure + 'Enegy Management - All weeks /'

color_palet = [united_colors[4],united_colors[4],united_colors[5],united_colors[5],
               'lightskyblue','lightskyblue','goldenrod','goldenrod']

legends = ['condition-based w/ storage','optimized w/ storage',
           'condition-based w/o storage','optimized w/o storage']

legends = None

x_label = 'Time [day]'

x = np.arange(1,len(cb_daily)+1)

for param_no in range(len(params)):
    param = params[param_no]

    y_label = y_labels[param_no]
    plot_title = param + ' - all days'
   
    

    Y_complete = [cb_daily[param],opt_daily[param]]
    width = 0.16

    bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                    save_figure=save_figure,path_saving_figure=path_saving_figure,plot_title=plot_title,
                    fs_legend = 24,fs_labels=32,fs_thicks=31,
                    dashed_bars_no=[1,3,5,7],color_palet=color_palet,ncol_leg=2)
    


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


# # test for loading
# with open(path_logging_data_results+'simulation_record_day_1.pkl', 'rb') as f:
#     loaded_dict = pickle.load(f)
# test = np.load(path_logging_data_results+'x_record_day_1'+'.npy') # loads your saved array into variable a.


# In[ ]:


params = ['cost_total [EUR]', 'profit_total [EUR]','m_f_MGT_NG [kg]','m_f_MGT_H2 [kg]',
         'P_prod_MGT [MW]','H2_produced [kg]','H2_tank_aval [kg]','MGT_V_pos [%]',
          'Q_prod_MGT [MW]','Q_waste [MW]','P_electrosis [MW]','P_balance_MG [MW]']

y_labels = ['Cost [EUR]','Profit/Loss [EUR]','$\mathdefault{m_{f,NG}}$' + ' [kg]','$\mathdefault{m_{f,H_{2}}}$' + ' [kg]',
           '$\mathdefault{{{{P}_M}_G}_T}}$' + ' [MW]','$\mathdefault{H_{2,produced}}$' + ' [kg]',
           '$\mathdefault{H_{2,available}}$' + ' [kg]','$\mathdefault{{{{V}_M}_G}_T}}$' + ' [%]',
           '$\mathdefault{{{{Q}_M}_G}_T}}$' + ' [MW]','$\mathdefault{{{{{{Q}_w}_a}_s}_t}_e}$' + ' [MW]',
           '$\mathdefault{{{{P}_E}_L}_Z}}$' + ' [MW]','$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]']



width = 0.25
save_figure = True


# In[ ]:


line_cycler   = (cycler(color=["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7", "#F0E442"]) +
                 cycler(linestyle=["-", "--", "-.", ":", "-", "--", "-."]))
marker_cycler = (cycler(color=["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7", "#F0E442"]) +
                 cycler(linestyle=["none", "none", "none", "none", "none", "none", "none"]) +
                 cycler(marker=["4", "2", "3", "1", "+", "x", "."]))

united_colors = ["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7", "#F0E442"]

united_colors = ['#2c7fb8','#1c9099','#000000', '#0000cd', '#e6194b', '#3cb44b', '#0082c8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',                 '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080', '#ffffff', '#000000']
united_colors = ['#252525','#000E9A', '#e6194b', '#3cb44b', '#0082c8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',                 '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080', '#ffffff', '#000000']



winter_descrete = ['#1300F5', '#0F2AE1', '#2254CD', '#0280BF', '#05ACA9', '#61D299', '#00FE7F']

orange_descrete = ['#EFCDBF', '#F3B29A', '#E0966D', '#D37D40', '#BD6F38', '#A35F2F']


# In[ ]:



# In[ ]:


params = ['cost_total [EUR]', 'profit_total [EUR]','m_f_MGT_NG [kg]','m_f_MGT_H2 [kg]',
         'P_prod_MGT [MW]','H2_produced [kg]','H2_tank_aval [kg]','MGT_V_pos [%]',
          'Q_prod_MGT [MW]','Q_waste [MW]','P_electrosis [MW]','P_balance_MG [MW]']

y_labels = ['Cost [EUR]','Profit/Loss [EUR]','$\mathdefault{m_{f,NG}}$' + ' [kg]','$\mathdefault{m_{f,H_{2}}}$' + ' [kg]',
           '$\mathdefault{{{{P}_M}_G}_T}}$' + ' [MW]','$\mathdefault{H_{2,produced}}$' + ' [kg]',
           '$\mathdefault{H_{2,available}}$' + ' [kg]','$\mathdefault{{{{V}_M}_G}_T}}$' + ' [%]',
           '$\mathdefault{{{{Q}_M}_G}_T}}$' + ' [MW]','$\mathdefault{{{{{{Q}_w}_a}_s}_t}_e}$' + ' [MW]',
           '$\mathdefault{{{{P}_E}_L}_Z}}$' + ' [MW]','$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]']




# saving_figure_path = path_saving_figure + 'Enegy Management - All weeks /'

color_palet = [united_colors[4],united_colors[4],united_colors[5],united_colors[5],
               'lightskyblue','lightskyblue','goldenrod','goldenrod']

legends = ['condition-based w/ storage','optimized w/ storage',
           'condition-based w/o storage','optimized w/o storage']

legends = None

x_label = 'Time [day]'

x = np.arange(1,len(opt_1_week_daily)+1)

for param_no in range(len(params)):
    param = params[param_no]

    y_label = y_labels[param_no]
    plot_title = param + ' - all weeks - 1 weeks version'
   
    

    Y_complete = [y_sc_1[param],y_opt[param],
                  y_sc_1_woH2[param],y_opt_woH2[param]]
    width = 0.16

    bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                    save_figure=True,path_saving_figure=path_saving_figure,plot_title=plot_title,
                    fs_legend = 24,fs_labels=32,fs_thicks=31,
                    dashed_bars_no=[1,3,5,7],color_palet=color_palet,ncol_leg=2)
    


# In[ ]:


params = ['m_f_MGT_H2 [kg]',
         'H2_produced [kg]','H2_tank_aval [kg]','P_electrosis [MW]']

y_labels = ['$\mathdefault{m_{f,H_{2}}}$' + ' [kg]',
           '$\mathdefault{H_{2,produced}}$' + ' [kg]',
           '$\mathdefault{H_{2,available}}$' + ' [kg]',
           '$\mathdefault{{{{P}_E}_L}_Z}}$' + ' [MW]']




# saving_figure_path = path_saving_figure + 'Enegy Management - All weeks /'

color_palet = [united_colors[4],united_colors[4]]

legends = ['condition-based','optimized']

legends = None


x_label = 'Time [day]'

x = np.arange(1,len(opt_1_week_daily)+1)

for param_no in range(len(params)):
    param = params[param_no]

    y_label = y_labels[param_no]
    plot_title = param + ' - all weeks - 1 weeks version'
   
    

    Y_complete = [y_sc_1[param],y_opt[param]]
    width = 0.2

    bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                    save_figure=True,path_saving_figure=path_saving_figure,plot_title=plot_title,
                    fs_legend = 24,fs_labels=32,fs_thicks=31,
                    dashed_bars_no=[1],color_palet=color_palet,ncol_leg=1)
    


# In[ ]:


params = ['El_Price_buy [EUR/kJ]', 'El_Price_sell [EUR/kJ]']

# y_labels = ['$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]',
#             '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
#             'Electricity Price Diff. [EUR/kJ]',
#            'Electricity-NG Price Diff. [EUR/kJ]']

# y_labels = ['$\mathdefault{{{{electricity Price buy}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]']  

y_labels = ['buy' ,
            'sell']  



# saving_figure_path = path_saving_figure + 'Enegy Management - All weeks /'

color_palet = [united_colors[2],united_colors[1]]

color_palet = ['lightcoral', 'cornflowerblue']
legends = [y_labels[0],y_labels[1]]

legends = None

x_label = 'Time [day]'

x = np.arange(1,len(opt_1_week_daily)+1)



y_label = 'Electricity Price [EUR/kJ]'
plot_title = 'Prices - all weeks - 1 week version'



Y_complete = [y_opt[params[0]],y_opt[params[1]]]
width = 0.2

bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                save_figure=True,path_saving_figure=path_saving_figure,plot_title=plot_title,
                fs_legend = 24,fs_labels=32,fs_thicks=31,
                dashed_bars_no=[],color_palet=color_palet,ncol_leg=1,scientific_y=True)
#     print(param, ':','week 9',y_opt_9[param].sum(),
#                      'week 15',y_opt_15[param].sum(),
#                      'week 16',y_opt_16[param].sum(),
#                      'week 26',y_opt_26[param].sum())


# In[ ]:


params = ['El_Price_NG_Price_diff [EUR/kJ]']

# y_labels = ['$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]',
#             '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
#             'Electricity Price Diff. [EUR/kJ]',
#            'Electricity-NG Price Diff. [EUR/kJ]']

# y_labels = ['$\mathdefault{{{{electricity Price buy}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]']  

y_labels = ['buy' ,
            'sell']  



# saving_figure_path = path_saving_figure + 'Enegy Management - All weeks /'

color_palet = [united_colors[2],united_colors[1]]

color_palet = ['lightcoral', 'cornflowerblue']
legends = [y_labels[0],y_labels[1]]
legends = None


x_label = 'Time [day]'

x = np.arange(1,len(opt_1_week_daily)+1)



y_label = 'El_Price_NG_Price_diff [EUR/kJ]'
plot_title = 'El_Price_NG_Prices - all weeks - 1 week version'



Y_complete = [y_opt[params[0]]]
width = 0.2

bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                save_figure=True,path_saving_figure=path_saving_figure,plot_title=plot_title,
                fs_legend = 24,fs_labels=32,fs_thicks=31,
                dashed_bars_no=[],color_palet=color_palet,ncol_leg=1,scientific_y=True)
#     print(param, ':','week 9',y_opt_9[param].sum(),
#                      'week 15',y_opt_15[param].sum(),
#                      'week 16',y_opt_16[param].sum(),
#                      'week 26',y_opt_26[param].sum())


# In[ ]:


params = ['El_Price_buy [EUR/kJ]', 'El_Price_sell [EUR/kJ]', 'NG_Price [EUR/kJ]']

# y_labels = ['$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]',
#             '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
#             'Electricity Price Diff. [EUR/kJ]',
#            'Electricity-NG Price Diff. [EUR/kJ]']

# y_labels = ['$\mathdefault{{{{electricity Price buy}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]']  

y_labels = ['El buy - El sell' ,
            'El sell - NG']  




color_palet = [united_colors[2],united_colors[1]]

color_palet = ['lightcoral', 'cornflowerblue']
legends = [y_labels[0],y_labels[1]]
legends = None


x_label = 'Time [day]'

x = np.arange(1,len(opt_1_week_daily)+1)



y_label = 'Price [EUR/kJ]'
plot_title = 'price differences'



Y_complete = [y_opt[params[0]]-y_opt[params[1]], y_opt[params[1]]- y_opt[params[2]]]
width = 0.2

bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                save_figure=True,path_saving_figure=path_saving_figure,plot_title=plot_title,
                fs_legend = 24,fs_labels=32,fs_thicks=31,
                dashed_bars_no=[],color_palet=color_palet,ncol_leg=1,scientific_y=True)
#     print(param, ':','week 9',y_opt_9[param].sum(),
#                      'week 15',y_opt_15[param].sum(),
#                      'week 16',y_opt_16[param].sum(),
#                      'week 26',y_opt_26[param].sum())


# In[ ]:


# params = ['P_prod_WT [MW]','P_dem [MW]','Q_dem [MW]','El_Price_diff [EUR/kJ]','El_Price_NG_Price_diff [EUR/kJ]']

params = ['P_dem [MW]','Q_dem [MW]','P_prod_WT [MW]']

# y_labels = ['$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]',
#             '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [MW]',
#             '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
#             'Electricity Price Diff. [EUR/kJ]',
#            'Electricity-NG Price Diff. [EUR/kJ]']

y_labels = ['$\mathdefault{{{{P}_D}_E}_M}}$' + ' [MW]',
            '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [MW]',
            '$\mathdefault{{{{P}_W}_T}}}$' + ' [MW]']         

           


color_palet = [united_colors[4],united_colors[5],'lightskyblue']

legends = [y_labels[0],y_labels[1],y_labels[2]]
legends = None


x_label = 'Time [day]'

x = np.arange(1,len(opt_1_week_daily)+1)



y_label = 'Energy [MW]'
plot_title = 'Energy - all weeks - 1 week version'



Y_complete = [y_opt[params[0]],y_opt[params[1]],y_opt[params[2]]]
width = 0.2

bar_diagram(x, Y_complete, x_label=x_label, y_label=y_label, legend=legends,width=width,
                save_figure=True,path_saving_figure=path_saving_figure,plot_title=plot_title,
                fs_legend = 25,fs_labels=32,fs_thicks=31,fs_values=20,show_value=True,
                x_lim=None,y_lim=[0,3],
                dashed_bars_no=[],color_palet=color_palet,ncol_leg=2)
#     print(param, ':','week 9',y_opt_9[param].sum(),
#                      'week 15',y_opt_15[param].sum(),
#                      'week 16',y_opt_16[param].sum(),
#                      'week 26',y_opt_26[param].sum())


# In[ ]:



# In[ ]:





# In[ ]:


week_optimized_data_path_week = week_optimized_data_path_week
optimized_performance_week = pd.read_excel(week_optimized_data_path_week,sheet_name='optimized')
scenario_1_performance_week = pd.read_excel(week_optimized_data_path_week,sheet_name='scenario 1')


# In[ ]:


path_saving_figure


# In[ ]:


# # day 1

# day_no = 1
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,60]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[0]]
# y2 = optimized_performance_week_day[params[1]]

# leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
# leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'

# legend = [leg1,leg2]
# Y = [y1,y2]
# x_label = 'Time [hr]'
# y_label = 'Demand [kW]'

# color_palet = [united_colors[4],united_colors[5],'lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_Q_dem', display_legend=legend)



# In[ ]:


# # day 2

# day_no = 2
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[0]]
# y2 = optimized_performance_week_day[params[1]]

# leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
# leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'

# legend = [leg1,leg2]
# Y = [y1,y2]
# x_label = 'Time [hr]'
# y_label = 'Demand [kW]'

# color_palet = [united_colors[4],united_colors[5],'lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_Q_dem', display_legend=[])



# In[ ]:


# # day 3

# day_no = 3
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[0]]
# y2 = optimized_performance_week_day[params[1]]

# leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
# leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'

# legend = [leg1,leg2]
# Y = [y1,y2]
# x_label = 'Time [hr]'
# y_label = 'Demand [kW]'

# color_palet = [united_colors[4],united_colors[5],'lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_Q_dem', display_legend=[])



# In[ ]:


# # day 4

# day_no = 4
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[0]]
# y2 = optimized_performance_week_day[params[1]]

# leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
# leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'

# legend = [leg1,leg2]
# Y = [y1,y2]
# x_label = 'Time [hr]'
# y_label = 'Demand [kW]'

# color_palet = [united_colors[4],united_colors[5],'lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_Q_dem', display_legend=[])



# In[ ]:


# # day 5

# day_no = 5
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[0]]
# y2 = optimized_performance_week_day[params[1]]

# leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
# leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'

# legend = [leg1,leg2]
# Y = [y1,y2]
# x_label = 'Time [hr]'
# y_label = 'Demand [kW]'

# color_palet = [united_colors[4],united_colors[5],'lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_Q_dem', display_legend=[])



# In[ ]:


# # day 6

# day_no = 6
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[0]]
# y2 = optimized_performance_week_day[params[1]]

# leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
# leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'

# legend = [leg1,leg2]
# Y = [y1,y2]
# x_label = 'Time [hr]'
# y_label = 'Demand [kW]'

# color_palet = [united_colors[4],united_colors[5],'lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_Q_dem', display_legend=[])



# In[ ]:


# # day 7

# day_no = 7
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[0]]
# y2 = optimized_performance_week_day[params[1]]

# leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
# leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'

# legend = [leg1,leg2]
# Y = [y1,y2]
# x_label = 'Time [hr]'
# y_label = 'Demand [kW]'

# color_palet = [united_colors[4],united_colors[5],'lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_Q_dem', display_legend=[])



# In[ ]:


# # day 1

# day_no = 1
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,230]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[2]]

# leg1 =  '$\mathdefault{{{{P}_W}_T}}}$'

# legend = [leg1]
# Y = [y1]
# x_label = 'Time [hr]'
# y_label = 'Wind Turbine Power [kW]'

# color_palet = ['lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_WT', display_legend=[])



# In[ ]:


# # day 2

# day_no = 2
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,230]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[2]]

# leg1 =  '$\mathdefault{{{{P}_W}_T}}}$'

# legend = [leg1]
# Y = [y1]
# x_label = 'Time [hr]'
# y_label = 'Wind Turbine Power [kW]'

# color_palet = ['lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_WT', display_legend=[])



# In[ ]:


# # day 3

# day_no = 3
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,230]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[2]]

# leg1 =  '$\mathdefault{{{{P}_W}_T}}}$'

# legend = [leg1]
# Y = [y1]
# x_label = 'Time [hr]'
# y_label = 'Wind Turbine Power [kW]'

# color_palet = ['lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_WT', display_legend=[])



# In[ ]:


# # day 4

# day_no = 4
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,230]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[2]]

# leg1 =  '$\mathdefault{{{{P}_W}_T}}}$'

# legend = [leg1]
# Y = [y1]
# x_label = 'Time [hr]'
# y_label = 'Wind Turbine Power [kW]'

# color_palet = ['lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_WT', display_legend=[])



# In[ ]:


# # day 5

# day_no = 5
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,230]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[2]]

# leg1 =  '$\mathdefault{{{{P}_W}_T}}}$'

# legend = [leg1]
# Y = [y1]
# x_label = 'Time [hr]'
# y_label = 'Wind Turbine Power [kW]'

# color_palet = ['lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_WT', display_legend=[])



# In[ ]:


# # day 6

# day_no = 6
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,230]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[2]]

# leg1 =  '$\mathdefault{{{{P}_W}_T}}}$'

# legend = [leg1]
# Y = [y1]
# x_label = 'Time [hr]'
# y_label = 'Wind Turbine Power [kW]'

# color_palet = ['lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_WT', display_legend=[])



# In[ ]:


# # day 7

# day_no = 7
# optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
# scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]
# y_lim=[0,230]
# x = np.arange(1,25)

# params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']

# y1 = optimized_performance_week_day[params[2]]

# leg1 =  '$\mathdefault{{{{P}_W}_T}}}$'

# legend = [leg1]
# Y = [y1]
# x_label = 'Time [hr]'
# y_label = 'Wind Turbine Power [kW]'

# color_palet = ['lightskyblue']


# simple_plotter(x, Y, 
#                x_label=x_label, y_label=y_label,
#                display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
#                color_palet=color_palet,
#                fs_legend = 25,fs_labels=32,fs_thicks=31,
#                ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
#                plot_title='Day'+str(day_no)+'_P_WT', display_legend=[])



# In[ ]:


# day 7

day_no = 7
optimized_performance_week_day = optimized_performance_week
scenario_1_performance_week_day = scenario_1_performance_week
y_lim=[-9,240]
x = np.arange(1,len(optimized_performance_week_day)+1)
x_show = np.linspace(0,len(optimized_performance_week_day),num=7+1)
params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]']


y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]

leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue']


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 20,fs_labels=20,fs_thicks=18,
               ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
               plot_title='Week_P_WT and P_dem and Q_dem', display_legend=legend,shape=[12, 3],x_show=x_show)



# In[ ]:


# day 7

day_no = 7
optimized_performance_week_day = optimized_performance_week
scenario_1_performance_week_day = scenario_1_performance_week
y_lim=[-9,110]
x = np.arange(1,len(optimized_performance_week_day)+1)

params = ['P_prod_MGT [kW]','P_electrosis [kW]']


y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]

leg1 =  '$\mathdefault{{P}_{MGT}}$'
leg2 =  '$\mathdefault{{P}_{ELZ}}}$'

legend = [leg1,leg2]
legends = None

Y = [y1,y2]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue']


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
               plot_title='Week_P_MGT and P_ELZ Optimized', display_legend=legend,shape=[12, 3])



# In[ ]:


# day 7

day_no = 7
optimized_performance_week_day = optimized_performance_week
scenario_1_performance_week_day = scenario_1_performance_week
y_lim=[-9,110]
x = np.arange(1,len(optimized_performance_week_day)+1)

params = ['P_prod_MGT [kW]','P_electrosis [kW]']


y1 = scenario_1_performance_week_day[params[0]].iloc[:168]
y2 = scenario_1_performance_week_day[params[1]].iloc[:168]

leg1 =  '$\mathdefault{{P}_{MGT}}$'
leg2 =  '$\mathdefault{{P}_{ELZ}}}$'

legend = [leg1,leg2]
legends = None

Y = [y1,y2]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue']


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
               plot_title='Week_P_MGT and P_ELZ scenario 1', display_legend=legend,shape=[12, 3])



# In[ ]:


# day 7

day_no = 7
optimized_performance_week_day = optimized_performance_week_noH2
scenario_1_performance_week_day = scenario_1_performance_week_noH2
y_lim=[-9,110]
x = np.arange(1,len(optimized_performance_week_day)+1)

params = ['P_prod_MGT [kW]','P_electrosis [kW]']


y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]

leg1 =  '$\mathdefault{{P}_{MGT}}$'
leg2 =  '$\mathdefault{{P}_{ELZ}}}$'

legend = [leg1,leg2]
legends = None

Y = [y1,y2]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue']


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[],leg_loc='best',y_lim=y_lim,
               plot_title='Week_P_MGT and P_ELZ Optimized no H2', display_legend=legend,shape=[12, 3])



# In[ ]:


# day 1

day_no = 1
optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)
y1 = scenario_1_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y2 = optimized_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y3 = optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]']/ optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]'].max()

leg1 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' condition-based'
leg2 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' optimized'
leg3 = 'electricity-NG price diff.'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Normalized Value [-]'

color_palet = [united_colors[0],united_colors[0],united_colors[1]]

simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[1],leg_loc='best',
               plot_title='Day'+str(day_no)+'_electrolyzer', display_legend=legend)



# In[ ]:


# day 2

day_no = 2
optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)
y1 = scenario_1_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y2 = optimized_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y3 = optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]']/ optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]'].max()

leg1 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' condition-based'
leg2 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' optimized'
leg3 = 'electricity-NG price diff.'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Normalized Value [-]'

color_palet = [united_colors[0],united_colors[0],united_colors[1]]

simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[1],leg_loc='best',
               plot_title='Day'+str(day_no)+'_electrolyzer', display_legend=legend)



# In[ ]:


# day 3

day_no = 3
optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)
y1 = scenario_1_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y2 = optimized_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y3 = optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]']/ optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]'].max()

leg1 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' condition-based'
leg2 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' optimized'
leg3 = 'electricity-NG price diff.'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Normalized Value [-]'

color_palet = [united_colors[0],united_colors[0],united_colors[1]]

simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[1],leg_loc='best',
               plot_title='Day'+str(day_no)+'_electrolyzer', display_legend=legend)



# In[ ]:


# day 4

day_no = 4
optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)
y1 = scenario_1_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y2 = optimized_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y3 = optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]']/ optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]'].max()

leg1 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' condition-based'
leg2 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' optimized'
leg3 = 'electricity-NG price diff.'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Normalized Value [-]'

color_palet = [united_colors[0],united_colors[0],united_colors[1]]

simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[1],leg_loc='best',
               plot_title='Day'+str(day_no)+'_electrolyzer', display_legend=legend)



# In[ ]:


# day 5

day_no = 5
optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)
y1 = scenario_1_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y2 = optimized_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y3 = optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]']/ optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]'].max()

leg1 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' condition-based'
leg2 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' optimized'
leg3 = 'electricity-NG price diff.'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Normalized Value [-]'

color_palet = [united_colors[0],united_colors[0],united_colors[1]]

simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[1],leg_loc='best',
               plot_title='Day'+str(day_no)+'_electrolyzer', display_legend=legend)



# In[ ]:


# day 6

day_no = 6
optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)
y1 = scenario_1_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y2 = optimized_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y3 = optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]']/ optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]'].max()

leg1 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' condition-based'
leg2 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' optimized'
leg3 = 'electricity-NG price diff.'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Normalized Value [-]'

color_palet = [united_colors[0],united_colors[0],united_colors[1]]

simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[1],leg_loc='best',
               plot_title='Day'+str(day_no)+'_electrolyzer', display_legend=legend)



# In[ ]:


# day 7

day_no = 7
optimized_performance_week_day = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)
y1 = scenario_1_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y2 = optimized_performance_week_day['P_electrosis [kW]']/ scenario_1_performance_week_day['P_electrosis [kW]'].max()
y3 = optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]']/ optimized_performance_week_day['El_Price_NG_Price_diff [EUR/kJ]'].max()

leg1 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' condition-based'
leg2 =  '$\mathdefault{{{{P}_E}_L}_Z}}$'+' optimized'
leg3 = 'electricity-NG price diff.'

legend = [leg1,leg2,leg3]
legends = None

Y = [y1,y2,y3]
x_label = 'Time [hr]'
y_label = 'Normalized Value [-]'

color_palet = [united_colors[0],united_colors[0],united_colors[1]]

simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=1,dashed=[1],leg_loc='best',
               plot_title='Day'+str(day_no)+'_electrolyzer', display_legend=legend)



# In[ ]:


# day 1 of week 
day_no = 1

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = scenario_1_performance_week_day[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - condition-based'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legends = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies', display_legend=legend)







# In[ ]:


# day 2 of week 
day_no = 2

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = scenario_1_performance_week_day[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - condition-based'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legends = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies', display_legend=legend)







# In[ ]:


# day 3 of week 
day_no = 3

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = scenario_1_performance_week_day[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - condition-based'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legends = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies', display_legend=legend)







# In[ ]:


# day 4 of week 
day_no = 4

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = scenario_1_performance_week_day[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - condition-based'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies', display_legend=legend)







# In[ ]:


# day 5 of week 
day_no = 5

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = scenario_1_performance_week_day[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - condition-based'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies', display_legend=legend)







# In[ ]:


# day 6 of week 
day_no = 6

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = scenario_1_performance_week_day[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - condition-based'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies', display_legend=legend)







# In[ ]:


# day 7 of week 
day_no = 7

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = scenario_1_performance_week_day[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - condition-based'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies', display_legend=legend)







# In[ ]:


# day 1 of week 
day_no = 1

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[6*24:7*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies_w&woELZ', display_legend=legend)






# In[ ]:


# day 2 of week 
day_no = 2

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[6*24:7*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies_w&woELZ', display_legend=legend)






# In[ ]:


# day 3 of week 
day_no = 3

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[6*24:7*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies_w&woELZ', display_legend=legend)






# In[ ]:


# day 4 of week 
day_no = 4

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[6*24:7*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies_w&woELZ', display_legend=legend)






# In[ ]:


# day 5 of week 
day_no = 5

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[6*24:7*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]

legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies_w&woELZ', display_legend=legend)






# In[ ]:


# day 6 of week 
day_no = 6

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[6*24:7*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies_w&woELZ', display_legend=legend)






# In[ ]:


# day 7 of week 
day_no = 7

optimized_performance_week_day = optimized_performance_week_noH2.iloc[(day_no-1)*24:day_no*24]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[(day_no-1)*24:day_no*24]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[6*24:7*24]

x = np.arange(1,25)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Day'+str(day_no)+'_energies_w&woELZ', display_legend=legend)






# In[ ]:


# day 7 of week 
day_no = 7

optimized_performance_week_day = optimized_performance_week_noH2.iloc[:168]
optimized_performance_week_day_wH2 = optimized_performance_week.iloc[:168]

scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[:168]

x = np.arange(1,169)

params = ['P_dem [kW]','Q_dem [kW]','P_prod_WT [kW]','P_balance_MG [kW]']

y1 = optimized_performance_week_day[params[0]]
y2 = optimized_performance_week_day[params[1]]
y3 = optimized_performance_week_day[params[2]]
y4 = optimized_performance_week_day_wH2[params[3]]
y5 = optimized_performance_week_day[params[3]]





leg1 =  '$\mathdefault{{{{P}_D}_E}_M}}$' + ' [kW]'
leg2 =  '$\mathdefault{{{{Q}_D}_E}_M}}$' + ' [kW]'
leg3 =  '$\mathdefault{{{{P}_W}_T}}}$' + ' [kW]'
leg4 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' w ELZ - optimized'
leg5 = '$\mathdefault{{{{P}_M}_G}}}$' + ' [MW]' + ' - optimized'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Week'+str(day_no)+'_energies_w&woELZ', display_legend=legend,shape=[12, 6])






# In[ ]:


optimized_performance_week_noH2


# In[ ]:


# day 7 of week 
day_no = 7


# optimized_performance_week_day = optimized_performance_week_noH2.iloc[:168]
# optimized_performance_week_day_wH2 = optimized_performance_week.iloc[:168]

# scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[:168]



# optimized_performance_week_day = optimized_performance_week_noH2.iloc[:168]
# optimized_performance_week_day_wH2 = optimized_performance_week.iloc[:168]

# scenario_1_performance_week_day = scenario_1_performance_week_noH2.iloc[:168]

x = np.arange(1,169)

params = ['P_electrosis [kW]','P_prod_MGT [kW]']

y1 = scenario_1_performance_week[params[0]].iloc[:168]
y2 = optimized_performance_week[params[0]].iloc[:168]
y3 = scenario_1_performance_week[params[1]].iloc[:168]
y4 = optimized_performance_week[params[1]].iloc[:168]
y5 = scenario_1_performance_week_noH2[params[1]].iloc[:168]

legends = ['condition-based w/ storage','optimized w/ storage',
           'condition-based w/o storage','optimized w/o storage']



leg1 =  '$\mathdefault{{{P}_{ELZ}}}$' + ' condition-based'
leg2 =  '$\mathdefault{{{P}_{ELZ}}}$' + ' optimized'
leg3 =  '$\mathdefault{{{P}_{MGT}}}$' + ' optimized w/ storage'
leg4 =  '$\mathdefault{{{P}_{MGT}}}$' + ' condition-based w/ storage'
leg5 =  '$\mathdefault{{{P}_{MGT}}}$' + ' optimized w/o storage'

legend = [leg1,leg2,leg3,leg4,leg5]
legend = None

Y = [y1,y2,y3,y4,y5]
x_label = 'Time [hr]'
y_label = 'Energy [kW]'

color_palet = [united_colors[4],united_colors[5],'lightskyblue',united_colors[0],united_colors[0]]


simple_plotter(x, Y, 
               x_label=x_label, y_label=y_label,
               display_plot_title=False,save_figure=True, save_figure_path=path_saving_figure,save_figure_resolution=1500,
               color_palet=color_palet,
               fs_legend = 25,fs_labels=32,fs_thicks=31,
               ncol_leg=2,dashed=[4],leg_loc='best',
               plot_title='Week'+str(day_no)+'_energies_w&woELZ', display_legend=legend,shape=[12, 6])






# In[ ]:



