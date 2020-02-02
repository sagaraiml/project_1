# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 12:03:03 2019

@author: sagar_paithankar
"""
import os
import pandas as pd
import pickle
from datetime import *

os.chdir(r'G:\Anaconda_CC\spyder\MySolar')
#==================Loading weather and power Raw df============================

wdf_pkl = open('weather_actual_AEMO_april_2019.pkl','rb')
rwdf = pickle.load(wdf_pkl)
wdf_pkl.close()

raw= open('raw_power_ghi_tillapril2019.pkl','rb')
pgdf = pickle.load(raw)
raw.close()
#==============================================================================
wcols = ['datetime_utc','sunrise','sunset',\
         'cloud_cover','dew_point','humidity','temperature','uv_index']
rwdf = rwdf[wcols]

#dtypes conversion
rwdf.iloc[:, 0:3] = rwdf.iloc[:, 0:3].apply(pd.to_datetime, errors='coerce')
pgdf['utc_datetime'] = pd.to_datetime(pgdf['utc_datetime'])
#converting to local time
for c in ['datetime_utc','sunrise','sunset']:
    rwdf[c]=rwdf[c]+timedelta(hours=8)
del c
#Changig name of column from datetime_utc to Time
rwdf.columns = ['Time', 'Sunise', 'Sunset', 'cloud_cover','dew_point','humidity','temperature','uv_index']
#converting to local time
pgdf['Time'] = pgdf['utc_datetime']+timedelta(hours=8)
#droping utc time column
pgdf.drop(columns='utc_datetime', inplace=True)

#setting time index
pgdf.set_index('Time', inplace=True)
#sorting df by index
pgdf.sort_index(inplace=True)
#removing outliers
pgdf = pgdf[pgdf['GHI'] >= 0] 
pgdf = pgdf[pgdf['Power'] >= 0]
#pgdf = pgdf[pgdf['Power'] >= 0]
#creating resampled df
pdf = pd.DataFrame()
#resampling data in 30mins
pdf['GHI'] = pgdf['GHI'].resample('30T').mean()
pdf['Power'] = pgdf['Power'].resample('30T').mean()
#sorting index
pdf.sort_index(inplace=True)
#reseting index
pdf.reset_index(inplace=True)
#creating time block
pdf['TB'] = pdf.Time.apply( lambda x : ((x.hour*60 + x.minute)//30+1))
#removing oulier (night time)
pdf = pdf[pdf['TB'].between(11, 41)]
pdf.set_index('Time', inplace=True)
#inderpolating for missing values on time base
pdfdetails = pd.DataFrame() #finding details
for col in pdf:
    pdf[col].interpolate(method='time', inplace=True)
    pdfdetails[col] = pdf.loc[:, col].describe()
del col
pdf.reset_index(inplace=True)

#removing outliers
rwdf = rwdf[rwdf['temperature'] >= rwdf['dew_point']]
rwdf = rwdf[rwdf['temperature'] >= 0]

weathercols = ['Time','cloud_cover','dew_point','humidity','temperature','uv_index']
weather = rwdf[weathercols]
weather.set_index('Time', inplace=True)
weather.sort_index(inplace=True)

wdf_res = pd.DataFrame()
wdetails = pd.DataFrame() #df to finding details

for col in weather:
    #resampling data in 30mins
    wdf_res[col] = weather[col].resample('30T').mean()
    #inderpolating for missing values on time base
    wdf_res[col].interpolate(method='time', inplace=True)
    wdetails[col] = weather.loc[:, col].describe()
del col

wdf_res.sort_index(inplace=True)

wdf_res.reset_index(inplace=True)

#deleting details of different df
del wdetails, pdfdetails
#creating df with power and weather details
df1 = pd.merge(pdf, wdf_res, on='Time', how='inner')

df1.set_index('Time', inplace=True)
#fetching details from df1
details_df1 = pd.DataFrame() #finding details
for col in df1:
    details_df1[col] = df1.loc[:, col].describe()
del col

df1.reset_index(inplace=True)

df_combine = open('df_combine.pkl', 'wb')
pickle.dump(df1, df_combine)
df_combine.close()
