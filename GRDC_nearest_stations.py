# -*- coding: utf-8 -*-





import os

import glob

import shutil

import numpy as np

import pandas as pd

from io import BytesIO

from zipfile import ZipFile

import matplotlib.pyplot as plt

from matplotlib import animation

from urllib.request import urlopen

from matplotlib.lines import Line2D

#from mpl_toolkits.basemap import Basemap



# %%





def extract_from_url(zipurl, path):

    """extract a zip file to the cwd given its url address

    """



    print('Fetching and unzipping file...')



    if not os.path.exists(path):

        os.makedirs(path)



    with urlopen(zipurl) as zipresp:

        with ZipFile(BytesIO(zipresp.read())) as zfile:

            zfile.extractall(path)





def parse_grdc_file(path):

    """import the grdc stations excel file to a pandas dataframe and

    convert a number of columns to the suitable data type

    """



    print('Parsing file...')



    filename = glob.glob('*GRDC_Stations.xlsx')[0]



    with open(filename, 'rb') as excelfile:

        data = pd.read_excel(excelfile, sheet_name='station_catalogue', index_col=0)



    num_cols = ['d_start', 'd_end', 'd_yrs', 'd_miss',

                'm_start', 'm_end', 'm_yrs', 'm_miss']



    #dt_cols = ['f_import', 'l_import']



    for column in num_cols:

        data[column] = pd.to_numeric(data[column], errors='coerce')



    #for column in dt_cols:

        #data[column] = pd.to_datetime(data[column], format='%d.%m.%Y')



    return data





def get_data_period(data):

    """return the measurement start and end years as well as the

    associated period

    """



    print('Establishing data period...')



    m_start = np.min(data['m_start'])

    m_end = np.max(data['m_end'])



    period = np.arange(m_start, m_end).astype(int)



    return m_start, m_end, period





def count_stations(data, period):

    """count the available grdc stations for a given year

    """



    print('Calculating yearly available stations...')



    stations = np.zeros_like(period)



    for index_p, year in enumerate(period):

        for index_s, station in enumerate(data.index):

            if (year >= data['m_start'].iloc[index_s] and

                    year <= data['m_end'].iloc[index_s]):

                stations[index_p] += 1



    return stations





def get_station_locations(data, period):

    """get the coordinates of the grdc stations operational in

    a given year

    """



    print('Processing available stations locations...')



    locations = {}



    for year in period:

        ls = []

        for index_s, station in enumerate(data.index):

            if (year >= data['m_start'].iloc[index_s] and

                    year <= data['m_end'].iloc[index_s]):

                lat = data['lat'].iloc[index_s]

                lon = data['long'].iloc[index_s]

                coors = (lon, lat)

                ls.append(coors)

        locations[year] = np.array(ls)



    return locations

def dist(lat1, long1, lat2, long2):
    return np.abs((lat1-lat2)+(long1-long2))

def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) *   np.sin(delta_lambda / 2)**2
    res = r * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))
    return np.round(res, 2)


    
    

def get_stations_same_region(data,period):
    stations_df = {}
    for year in period:

        

        for index_s, station in enumerate(data.index):
            if (year >= data['m_start'].iloc[index_s] and

                    year <= data['m_end'].iloc[index_s]):
                #print(station)
                #print("---")
                station_region = data['sub_reg'].iloc[index_s]
                station_lat = data['lat'].iloc[index_s]
                station_long = data['long'].iloc[index_s]
                station_name = data['station'].iloc[index_s]
                matches = data.loc[(data['sub_reg'] == station_region) & (data['station'] != station_name),('lat','long')]
                #print(matches.head())
                distances = matches.apply( lambda row: haversine_distance(station_lat, station_long, row['lat'], row['long']), axis=1)
                
                #print(distances.values.tolist())
                #distances_list = distances.values.tolist()
                #distances_list = sorted(distances_list, key=lambda x:float(x))
                horizontal_stack = pd.concat([matches,distances],axis=1)
                horizontal_stack.rename(columns={0:'d'},inplace=True)
                #print(horizontal_stack.head())
                sorted_horizontal_stack = horizontal_stack.sort_values(by=['d'], ascending=True)
                #print(sorted_horizontal_stack.head())
                #print(list(matches.columns.values))
                
                #station_list = matches.index.map(str).to_list()
                station_list = sorted_horizontal_stack.index.map(str).to_list()
                print(station_list)
                print("\n")
                stations_df[station]= station_list
    

    return stations_df
    


# %%



if __name__ == '__main__':



    

    path = os.getcwd()

    #extract_from_url(zipurl, path)

    data = parse_grdc_file(path)
    new_df = data.loc[data['wmo_reg']==3]
    #new_df.to_csv('region3_stations.csv',sep=',',encoding='utf-8',index=False)
    #print(len(new_df))

    m_start, m_end, period = get_data_period(new_df)

    stations = count_stations(new_df, period)

    locations = get_station_locations(new_df, period)

    stations_dict = get_stations_same_region(new_df,period)
    
    stations_df = pd.DataFrame.from_dict(stations_dict, orient='index')
    #stations_df.to_csv('nearby_stations.csv',sep=',',encoding='utf-8',index=False)

    