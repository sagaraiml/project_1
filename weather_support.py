# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 17:53:04 2019

@author: sagar_paithankar
"""

class weather:
    
    #Weather token function
    def get_token(self):
        username = "tech@dummy.com"
        password = "dentintheuniverse"
        base_url = "http://apihub.dummy.com/api"
        try:
           headers = {}
           params = {'username': username, 'password': password}
           
           api_token = base_url + "/get-token"
           
           r = requests.post(url=api_token, headers=headers, params=params)
           return r.json()
       
        except Exception as e:
            print("Error in fetching weather token : {a}".format(a=e))

    #Fetch actual weather data and return a processed dataframe
    def combiner1(self, start_date, end_date, plant_id, client_id, source):
    
        url = "http://apihub.dummy.com/api/weather/getActual"
        querystring = {"from-date":start_date,"to-date":end_date,"plant-id":plant_id,"client_id":client_id,"source":source}
        headers = {'token': weather().get_token()['access_token']}
        
        try:
            response = requests.post(url, headers=headers, params=querystring)
            """
            headers = {'token': "$2y$10$q8SasTBbnyIqHXQ7eQpXY.N.IwpLj6txoh56.mzwAoXZYICGhcScK",
                   'cache-control': "no-cache",
                   'postman-token': "013c7a7d-eb47-b3ff-45d5-ad338724c449"}
            response = requests.request("POST", url, headers=headers, params=querystring)
            """
            data=response.json()
            d=pd.DataFrame(data['data'])
            d=d[['datetime_local', 'apparent_temperature', 'temperature', 'humidity', 'dew_point', 'wind_speed', 'cloud_cover']]
            d.rename(columns={'datetime_local': 'datetime'}, inplace=True)
            d['datetime']=pd.to_datetime(d['datetime'])
            if (type(d.temperature[1]) == str) or (type(d.apparent_temperature[1]) == str) or (type(d.humidity[1]) == str):
                d=d.replace('Null', np.nan)
                d['apparent_temperature']=d['apparent_temperature'].apply(lambda x: (float(x.replace("'", ''))))
                d['temperature']=d['temperature'].apply(lambda x: (float(x.replace("'", ''))))
                d['humidity']=d['humidity'].apply(lambda x: (float(x.replace("'", ''))))
                d['dew_point']=d['dew_point'].apply(lambda x: (float(x.replace("'", ''))))
                d['wind_speed']=d['wind_speed'].apply(lambda x: (float(x.replace("'", ''))))
                d['cloud_cover']=d['cloud_cover'].apply(lambda x: (float(x.replace("'", ''))))
            else:
                d=d
            d=d.replace('Null', np.nan)
            d.dropna(inplace=True)
            wdf=d
            wdf['datetime'] = pd.to_datetime(wdf.datetime)
            wdf.iloc[:,1:] = wdf.iloc[:,1:].astype(float)
        
            wdf = wdf.drop_duplicates('datetime')
            wdf.loc[wdf['temperature'] < 0, 'temperature'] = np.nan
            wdf.loc[wdf.temperature.isnull(), 'dew_point'] = np.nan
            wdf.loc[wdf.temperature.isnull(), 'apparent_temperature'] = np.nan
            wdf.loc[wdf.temperature.isnull(), 'humidity'] = np.nan
            wdf.loc[wdf.temperature.isnull(), 'wind_speed'] = np.nan
            wdf.loc[wdf.temperature.isnull(), 'cloud_cover'] = np.nan
            wdf.set_index('datetime', inplace=True)
            wdf = wdf.interpolate(method='time')
            wdf = wdf.resample('15min').asfreq()
#            wdf = wdf.fillna(method='ffill', limit=1)
#            wdf = wdf.fillna(method='bfill', limit=1)
            wdf = wdf.interpolate(method='time')
            wdf.reset_index(inplace=True)
            wdf = wdf.drop_duplicates('datetime')
            wdf.reset_index(inplace=True,drop=True)
            return wdf
        
        except Exception as e:
                print("Error in fetching weather actuals data : {a}".format(a=e))
    
    #Fetch weather forecast data from source specified in argument
    def combiner(self, start_date, end_date, plant_id, client_id, source):
        
        url = "http://apihub.dummy.com/api/weather/getForecast"
        if source=='accuweather_forecast':
            querystring = {"from-date":start_date,"to-date":end_date,"plant-id":plant_id,"client_id":client_id,"source":source,"type":'240_hours'}
       # elif source=='combiner_forecast':
        #    querystring = {"from-date":start_date,"to-date":end_date,"plant-id":plant_id,"client_id":client_id,"source":source,"type":'optimiser'}
        else :
            querystring = {"from-date":start_date,"to-date":end_date,"plant-id":plant_id,"client_id":client_id,"source":source}
        headers = {'token': weather().get_token()['access_token']}
        
        try:
            response = requests.post(url, headers=headers, params=querystring)
            """
            headers = {'token': "$2y$10$q8SasTBbnyIqHXQ7eQpXY.N.IwpLj6txoh56.mzwAoXZYICGhcScK",
                   'cache-control': "no-cache",
                   'postman-token': "013c7a7d-eb47-b3ff-45d5-ad338724c449"}
            response = requests.request("POST", url, headers=headers, params=querystring)
            """
            data=response.json()
            l=pd.DataFrame(data['data'])
            l['datetime']=pd.to_datetime(l['datetime_local'])
            l=l.sort_values(by=['datetime'])
            l=l.reset_index(drop=True)
            l.set_index('datetime', inplace=True)
            l = l.interpolate(method='time')
            l = l.resample('15min').asfreq()
#            l = l.fillna(method='ffill', limit=1)
#            l = l.fillna(method='bfill', limit=1)
            l = l.interpolate(method='time')
            l.reset_index(inplace=True)
            l = l.drop_duplicates('datetime')
            l = l[['datetime', 'apparent_temperature', 'temperature', 'humidity', 'dew_point', 'wind_speed', 'cloud_cover']]
            return l
        
        except Exception as e:
                print("Error in fetching weather forecast data : {a}".format(a=e))