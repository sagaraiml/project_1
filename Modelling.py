# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 16:45:11 2019

@author: sagar_paithankar
"""

import os
import pandas as pd
import pickle
from datetime import *
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as image
import numpy as np
pd.options.mode.chained_assignment = None
os.chdir(r'G:\Anaconda_CC\spyder\MySolar')
#====================Loading combined df==============================
infile = open('Input_df_Model.pkl','rb')
To_model = pickle.load(infile)
infile.close()
#modifying df so will predict on 2019 data and train till 2018-12-31 
#doing operation on data till 2018-12-31
df = To_model[(To_model["Time"] < datetime.strptime('2019-01-01', '%Y-%m-%d'))]
df.set_index('Time', inplace=True)
df.sort_index(inplace=True)
df = df.drop_duplicates()
details1 = pd.DataFrame()
for col in df:
    details1[col] = df.loc[:, col].describe()
del col
shape1 = df.shape
df.reset_index(inplace=True)


cols = ['Time', 'GHI', 'Power', 'cloud_cover', 'dew_point', 'humidity',
        'temperature', 'uv_index', 'lag1b', 'lag2b', 'lag3b',
        'lag1', 'lag2', 'lag3', 'Power_wm2h', 'Power_wm4h', 'Power_wm8h',
        'Power_wm24h', 'sin_doy', 'sin_tb', 'sin_month']

features = ['Time', 'GHI', 'Power','lag1b', 'lag2b', 'lag3b',\
        'lag1', 'lag2', 'lag3', 'Power_wm2h', 'Power_wm4h', 'Power_wm8h',\
        'Power_wm24h', 'sin_doy', 'sin_tb', 'sin_month',\
        'cloud_cover', 'dew_point', 'humidity', 'temperature', 'uv_index']

shift_features = ['cloud_cover', 'dew_point', 'humidity', 'temperature', 'uv_index']

target_horizons = [30]
model_type = 'xgboost'
validation_period = 5

start = datetime.strptime('2019-01-01 05:00:00', '%Y-%m-%d %H:%M:%S')

def get_date(timedel):
    dt = (start + timedelta(days=timedel)).strftime('%Y-%m-%d %H:%M:%S')
    return dt


def train(df,features,shift_feature,target_horizons,model_type,validation_period):
    df3=df.copy()
    for i in target_horizons:
        try:
            print('Training on {a} for {b} day ahead'.format(a=model_type,b=int(i/30)))
            df4 = df3[features]
            df4['target'] = df4.Power.shift(-i) 
        
            for j in shift_features:
                df4[j] = df4[j].shift(-i)
            print('Shifting selected features: by {b} blocks'.format(b=i))
        
            df4.dropna(inplace=True)
            x, y = df4.drop('target',1).copy(), df4[['Time','target']].copy()
        
            x_train, y_train = x[x['Time'] < get_date(0)], y[y['Time'] < get_date(0)]
        
            ind2=df4[df4['Time'] >= pd.to_datetime((df4['Time'][len(df4['Time'])-1]).date()- timedelta(days=validation_period))]
#           ind2=ind2.reset_index(drop=True)
            xv, yv = ind2.drop('target',1).copy(), ind2[['Time','target']].copy()
        
            x_train=x_train[x_train['Time']<=pd.to_datetime((df4['Time'][len(df4['Time'])-1]).date()- timedelta(days=validation_period))]
            y_train=y_train[y_train['Time']<=pd.to_datetime((df4['Time'][len(df4['Time'])-1]).date()- timedelta(days=validation_period))]
        
            x_train, y_train = x_train.iloc[:,1:], y_train.iloc[:,-1]
            xv, yv = xv.iloc[:,1:], yv.iloc[:,-1]
            
#            categorical_features_indices=list(misc().column_index(x_train, categorical_features))
        except Exception as e:
            print("Error setting up training data structure for target horizon {b} due to : {a}".format(a=e,b=i))
            
        try:
            if model_type == 'xgboost':
                import xgboost as xgb
                data_matrix = xgb.DMatrix(x_train, label=y_train)
                data_matrixv = xgb.DMatrix(xv, label=yv)
                   #'n_estimators':200  >> did not see this
                params = {'n_estimators':200,'objective':'reg:linear','booster':'gbtree','max_depth':10,'learning_rate':0.04,\
                'colsample_bytree':0.6,'colsample_bylevel':0.6,'subsample':0.8,'min_child_weight':1,'gamma':1}
        
                model = xgb.train(params, data_matrix,num_boost_round=2000,evals=[(data_matrixv, "Test")],early_stopping_rounds=15)
        except Exception as e:
            print("Error setting up final {c} model data matrices for target horizon {b} due to : {a}".format(a=e,b=i,c=model_type))
            
        pickle.dump(model, open(path+'/'+model_type+'_'+str(i)+'.pkl', 'wb'))
        
        
train(df,features,shift_features,target_horizons,model_type,validation_period)