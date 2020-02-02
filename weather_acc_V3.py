# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 18:29:25 2019

@author: sagar_paithankar
"""

"""
nehru client 8 : plant 13
plant client 30 : plantid  : 1

UP cliend id 37
plant_list = [[5, "Agra"], [6, "Aligarh"], [4, "Allahabad"], [7, "Bareilly"],
[3, "Ghaziabad"], [8, "Gorakhpur"], [9, "Jhansi"], [2, "Kanpur"], [1, "Lucknow"],
 [10, "Meerut"], [12, "Moradabad"], [13, "Noida"],[14, "Saharanpur"], [15, "Varanasi"]]
"""

import os
import pandas as pd
import numpy as np
from datetime import *
import numpy as np
import time
from brpl_support import *
#path = '/home/Weather_accuracy'
#os.chdir(path)
os.chdir(r'G:\Anaconda_CC\spyder\weather')
os.environ['TZ'] = 'Asia/Calcutta'
#time.tzset()
pd.options.mode.chained_assignment = None

sd = str(datetime.date(datetime.now() - timedelta(days=1)))
cols = ['apparent_temperature', 'temperature','humidity','dew_point', 'wind_speed', 'cloud_cover']
actu = pd.DataFrame()
# =============================================================================
# #Fetch actual weather data and return a processed dataframe
# def combiner1(self, start_date, end_date, plant_id, client_id, source):
# #Fetch weather forecast data from source specified in argument
# def combiner(self, start_date, end_date, plant_id, client_id, source):
# =============================================================================
client_deatils = {'Name':'Pitampura', 'client_id' : 30, 'plant_id' : 1}
client_deatils1 = {'Name':'Nehru','client_id' : 8, 'plant_id' : 13}

def weather_accurancy(client_deatils, cols):
    fore = pd.DataFrame()
    MAE_df = pd.DataFrame()
    d = {}
    
    actu = weather().combiner1(sd, sd, client_deatils['plant_id'], client_deatils['client_id'], 'darksky_actual')
    fore = weather().combiner(sd, sd, client_deatils['plant_id'], client_deatils['client_id'], 'combiner_forecast')
    MAE_df = pd.merge(actu, fore, on='datetime', how='inner')['datetime']
    actu = actu.iloc[:len(MAE_df), :]
    fore = fore.iloc[:len(MAE_df), :]

    for col in cols:
        MAE_df[col] = np.where( actu[col] > 0 ,np.abs(100*(actu[col] - fore[col])/actu[col]) ,0)
        d.update({col : MAE_df[col].mean()})
    #    MAE_df[col].dropna(inplace=True)
        details = pd.DataFrame(d, index = [sd])
        details['Name'] = [client_deatils['Name']]
        details['Name'] = details['Name'].astype('category')      
    return details


accu = weather_accurancy(client_deatils, cols)
accu = accu.append(weather_accurancy(client_deatils1, cols))

# =============================================================================
# =============================================================================
client_id = 37
plant_list = [[5, "Agra"], [6, "Aligarh"], [4, "Allahabad"], [7, "Bareilly"],
              [3, "Ghaziabad"], [8, "Gorakhpur"], [9, "Jhansi"], [2, "Kanpur"], [1, "Lucknow"],
              [10, "Meerut"], [12, "Moradabad"], [13, "Noida"],[14, "Saharanpur"], [15, "Varanasi"]]


def weather_accurancy_UPlike(client_id, plant, cols):
    actu = pd.DataFrame()
    fore = pd.DataFrame()
    MAE_df = pd.DataFrame()
    d = {}
    
    actu = weather().combiner1(sd, sd, int(plant[0]), client_id, 'darksky_actual')
    if len(actu) > 0:
        print('actu came for {a}'.format(a=plant[1]))
    else:
        print('actu not came')
    fore = weather().combiner(sd, sd, int(plant[0]), client_id, 'wunderground_forecast')
    if len(fore) > 0:
        print('fore came for {a}'.format(a=plant[1]))
    else:
        print('actu not came')
    
    MAE_df = pd.merge(actu, fore, on='datetime', how='inner')['datetime']
    actu = actu.iloc[:len(MAE_df), :]
    fore = fore.iloc[:len(MAE_df), :]
        
    for col in cols:
        MAE_df[col] = np.where( actu[col] > 0 ,np.abs(100*(actu[col] - fore[col])/actu[col]) ,0)
#        MAE_df[col] = np.where( actu[col] == 0 ,np.abs(100*(actu[col] - fore[col])) ,np.abs(100*(actu[col] - fore[col])/actu[col]))
#        MAE_df[col] = np.abs(100*(actu.loc[:,col] - fore.loc[:,col])/actu.loc[:,col])
        d.update({col : MAE_df[col].mean()})
        details = pd.DataFrame(d, index = [sd])
        details['Name'] = [plant[1]]
        details['Name'] = details['Name'].astype('category')
    
    print('done for {a}'.format(a=plant[1]))    
    return details

for plant in plant_list:
    details = weather_accurancy_UPlike(client_id, plant, cols)
    accu = accu.append(details)

Total = accu.T

'''
body_str = ""
body_str += "<br>"
body_str += "Weather accuracy MAPE For - " +(datetime.now().date() - timedelta(1)).strftime("%Y-%m-%d")+":" 
body_str += "<br>"
body_str += "<br>"
body_str += "<br>"
body_str += "<br>"
body_str += Total.to_html()
body_str += "<br>"
body_str += "<br>"
body_str += "<br>"
body_str += "<br>" 
#

drq= {"to":["sagar.paithankar@dummy.com", "modeller@dummy.com"],"from":"mailbot@dummy.com","subject":"","body":""}
drq['subject'] ="Weather accuracy MAPE -  "+str(datetime.now().date())
drq['body'] = body_str
drq['type'] = 'html'
jsdrq=json.dumps(drq)
r = requests.post("http://api.dummy.com/index.php?r=notifications/send-email", headers = {'Content-type': 'application/json', 'Accept': 'text/plain'},data= jsdrq)
print("Mailing Success")
'''