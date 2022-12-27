import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import inflection
import scipy.stats as ss
import math


from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import RobustScaler, MinMaxScaler, LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error,mean_absolute_percentage_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Lasso, Ridge
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor

from IPython.core.display import HTML
from IPython.display import Image
import datetime

import random
import warnings


def cramer_v(x, y):
    cm = pd.crosstab(x, y)
    return ss.contingency.association(cm, method='cramer', correction=True)

def note_settings():
    #%matplotlib inline
    

    plt.style.use('bmh')
    plt.rcParams['figure.figsize'] = [25, 12]
    plt.rcParams['font.size'] = 24

    display(HTML('<style>.container {width: 100% !important; }</style>'))
    pd.options.display.max_columns = None
    pd.set_option('display.expand_frame_repr', False)

    sns.set()

# Machine Learning Metrics Results
def ml_error(model_name, y, yhat):
    mae = mean_absolute_error(y, yhat)
    mape = mean_absolute_percentage_error(y, yhat)
    # RMSE - pode ficar bastante elevado devido a presença de outliers (pode auxiliar nesse diagnóstico). Quando o erro é pequeno o RMSE é menor que o MAE
    rmse = np.sqrt(mean_squared_error(y, yhat))

    return pd.DataFrame({'Model Name': model_name,
                        'MAE': mae,
                        'MAPE': mape,
                        'RMSE': rmse}, index=[0])


# Cross Validation
def cross_valid_timeseries(x_training, kfold, model_name, model, verbose=False):

    mae_list = []
    mape_list = []
    rmse_list = []
    for k in range(kfold, 0, -1):
        if verbose:
            print(f'\nKFold Number: {k}')
        # Start and end date for validation
        valid_start_date = x_training['date'].max() - datetime.timedelta(days=k*6*7)
        valid_end_date = x_training['date'].max() - datetime.timedelta(days=(k-1)*6*7)

        # Filtering dataset

        training = x_training[x_training['date'] < valid_start_date]
        validation = x_training[(x_training['date'] >= valid_start_date) & (x_training['date'] <= valid_end_date)]

        # Trainin and validation dataset

        xtraining = training.drop(['date', 'sales'], axis= 1)
        ytraining = training['sales']

        xvalidation = validation.drop(['date', 'sales'], axis= 1)
        yvalidation = validation['sales']

        # model
        m = model.fit(xtraining, ytraining)

        # prediction
        yhat_m_val = m.predict(xvalidation)
        
        # performance
        m_val_result = ml_error('Linear Regression', np.expm1(yvalidation), np.expm1(yhat_m_val))

        mae_list.append(m_val_result['MAE'])
        mape_list.append(m_val_result['MAPE'])
        rmse_list.append(m_val_result['RMSE'])
        

    mae_p = str(np.round(np.mean(mae_list), 2)) + ' +/- ' + str(np.round(np.std(mae_list)))

    mape_p = str(np.round(np.mean(mape_list), 2)) + ' +/- ' + str(np.round(np.std(mape_list)))
    rmse_p = str(np.round(np.mean(rmse_list), 2)) + ' +/- ' + str(np.round(np.std(rmse_list)))

    return pd.DataFrame({'Model': model_name, 'MAE': mae_p, 'MAPE': mape_p, 'RMSE': rmse_p}, index=[0])

def mean_percentage_error(y, yhat):
    return np.mean((y - yhat)/y)