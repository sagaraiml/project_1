# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 16:58:27 2019

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

os.chdir(r'G:\Anaconda_CC\spyder\MySolar')
#====================Loading combined df==============================
infile = open('df_combine.pkl','rb')
rdf = pickle.load(infile)
infile.close()

#['GHI', 'Power', 'TB', 'cloud_cover', 'dew_point', 'humidity','temperature', 'uv_index'],
"""
negative  >> humidity, dew_point, cloud_cover
positive >> GHI, temperature, uv_index
"""
# An "interface" to matplotlib.axes.Axes.hist() method
def freq(dseries):
    n, bins, patches = plt.hist(x=dseries, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('My Very Own Histogram')
    return None

def sinwave(df, feat, divs):
    return np.sin(df[str(feat)]*(2*np.pi/divs))

print('Adding lags...')
rdf['doy'] = rdf.Time.dt.dayofyear
rdf['month'] = rdf.Time.dt.month
rdf['lag1b'] = rdf.Power.shift(1)
rdf['lag2b'] = rdf.Power.shift(2)
rdf['lag3b'] = rdf.Power.shift(3)
rdf['lag1'] = rdf.Power.shift(48)
rdf['lag2'] = rdf.Power.shift(96)
rdf['lag3'] = rdf.Power.shift(148)
print('Added 8 features')

print('Adding ewms for load...')
rdf['Power_wm2h'] = rdf['Power'].ewm(span=4).mean()
rdf['Power_wm4h'] = rdf['Power'].ewm(span=8).mean()
rdf['Power_wm8h'] = rdf['Power'].ewm(span=16).mean()
rdf['Power_wm24h'] = rdf['Power'].ewm(span=48).mean()
print('Added 4 ewm')



print('Adding sine derivatives to time variables...')
rdf['sin_doy'] = sinwave(rdf, 'doy', 365)
rdf['sin_tb'] = sinwave(rdf, 'TB', 30)
rdf['sin_month'] = sinwave(rdf, 'month', 12)

rdf.dropna(inplace=True)

rdf.set_index('Time', inplace=True)
rdf.sort_index(inplace=True)
rdf = rdf.drop_duplicates()

freq(rdf['doy'])
freq(rdf['sin_doy'])
freq(rdf['TB'])
freq(rdf['sin_tb'])
freq(rdf['month'])
freq(rdf['sin_month'])

details1 = pd.DataFrame()
for col in rdf:
    details1[col] = rdf.loc[:, col].describe()
del col
shape1 = rdf.shape
rdf.reset_index(inplace=True)

rdf.set_index('Time', inplace=True)




# =============================================================================
# outliers >>
# CC<0.35 and still GHI/Power negligible
# In Summer CC<0.35 and still GHI/Power negligible
# Winter removing morning hours
# sunshine hours and CC < 0.35 still power/GHI negligible
# =============================================================================

#logic >> CC negligiible but still Power/GHI zero
#GHI or Power Zero when cloud_cover is not 
remo1 = rdf[((rdf['GHI'] == 0 ) & (rdf['Power'] == 0 )) & rdf['cloud_cover'].between(0, 0.25)]

#Logic >> CC negligiible in summer still Power&GHI negligible
#GHI/Power negligiible when cloud_cover is not that much but sunny period of year
remo2 = rdf[( (rdf['GHI'] < 1) & (rdf['Power'] < 0.1) ) &
        ((rdf['month'].between(9,12)) | (rdf['month'].between(1,4))) &
        rdf['cloud_cover'].between(0, 0.25)]

#logic >> Sunset and Sunrise time is Moved so removing NON-SUNNY Hours from April to Sept
remo3 = rdf[( (rdf['GHI'] < 1) | (rdf['Power'] < 0.1) ) &\
            (rdf['TB'].between(11,16) | rdf['TB'].between(34,41)) &\
            (rdf['month'].between(4,9)) ]

#logic >> CC is negligible still GHI or Power zero and Time 5am to 10am and 4pm to 8pm
remo4 = rdf[( (rdf['GHI'] < 1) | (rdf['Power'] < 0.1) ) &\
            rdf['TB'].between(18,34)&\
            rdf['cloud_cover'].between(0, 0.25)]

# =============================================================================
# #logic >> CC is negligible in day time and still GHI/Power is zero
# #9am to 4pm GHI or Power Zero but Clouds are not zero
# remo_subset = rdf[( (rdf['GHI'] == 0) | (rdf['Power'] == 0) ) &\
#             (rdf['TB'].between(19,33)) &\
#             rdf['cloud_cover'].between(0, 0.3)]
# 
# #remo_subset will be subset of remo1
# =============================================================================

freq(remo3['cloud_cover'])
freq(remo3['TB'])
freq(remo1['TB'])

freq(rdf['Power'])
freq(rdf['TB'])
freq(rdf['month'])
freq(rdf['sin_month'])

#==============================================================================
#kind must be either 'c', 'reg', 'resid', 'kde', or 'hex'
# =============================================================================
# sns.jointplot(data=remo1, x='cloud_cover', y='Power', kind='hex', color='g')
# 
# sns.jointplot(data=rdf, x='GHI', y='Power', kind='hex', color='g')
# 
# sns.distplot(l.cloud_cover)
# sns.distplot(l['TB'],bins="doane",kde=False, color='g')
# plt.scatter(x=l['TB'], y=l['Power'])
# sns.jointplot(data=rdf, x='GHI', y='Power', kind='reg', color='g')
# sns.jointplot(data=rdf, x='TB', y='Power', kind='reg', color='g')
# =============================================================================
#==============================================================================



#removing rows having above condition >> removing outlier
rdf = pd.concat([rdf, remo1, remo2, remo3, remo4]).drop_duplicates(keep=False)
shape2 = rdf.shape

details2 = pd.DataFrame()
for col in rdf:
    details2[col] = rdf.loc[:, col].describe()
del col

rdf.drop(columns=['doy', 'month','TB'], inplace=True)

rdf.reset_index(inplace=True)

for_model = open('Input_df_Model.pkl', 'wb')
pickle.dump(rdf, for_model)
for_model.close()

#----------------------------------------------
f = sample["Time"] < datetime.strptime('2019-01-01', '%Y-%m-%d %H:%M:%S')
saample.where(f, inplace=True)