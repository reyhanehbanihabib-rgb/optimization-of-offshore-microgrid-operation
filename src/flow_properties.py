#!/usr/bin/env python
# coding: utf-8

# In[7]:


import numpy as np
import pandas as pd
import math
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d
from scipy.interpolate import CubicSpline
import scipy.integrate as integrate
from scipy.integrate import quad
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

from sklearn import linear_model


# To plot pretty figures
import matplotlib as mpl
import matplotlib.pyplot as plt
from src.paths import DATA_ROOT, require_path


# In[2]:


thermophysical_data = require_path(DATA_ROOT / "thermophysical properties of flows.xlsx")

xls = pd.ExcelFile(thermophysical_data)
methane_data = pd.read_excel(xls, 'methane')
hydrogen_data = pd.read_excel(xls, 'hydrogen')


# In[3]:


def polynomial(df, x_label, y_label, selected_degree):
    poly = PolynomialFeatures(degree=selected_degree)
    X = df[x_label]
    y = df[y_label] 
    poly_variables = poly.fit_transform(X)
    poly_var_train, poly_var_test, res_train, res_test = train_test_split(poly_variables, y, test_size = 0.2, random_state = 4)
    regression = linear_model.LinearRegression()
    model = regression.fit(poly_var_train, res_train)
    score = model.score(poly_var_test, res_test)
    coefs = model.coef_
    intercept = model.intercept_
    return coefs, intercept, poly



# In[4]:


cp_methane_coefs, cp_methane_intercept, cp_methane_poly = polynomial(methane_data, ['Temperature (K)', 'Pressure (bar)'], 'Cp (J/g*K)', 3)
cv_methane_coefs, cv_methane_intercept, cv_methane_poly = polynomial(methane_data, ['Temperature (K)', 'Pressure (bar)'], 'Cv (J/g*K)', 3)
cp_hydrogen_coefs, cp_hydrogen_intercept, cp_hydrogen_poly = polynomial(hydrogen_data, ['Temperature (K)', 'Pressure (bar)'], 'Cp (J/g*K)', 3)
cv_hydrogen_coefs, cv_hydrogen_intercept, cv_hydrogen_poly = polynomial(hydrogen_data, ['Temperature (K)', 'Pressure (bar)'], 'Cv (J/g*K)', 3)

