# cleaning script for flight delay data
# abraae sept 2021

# load libraries --------------------------------------------------
import pandas as pd
import numpy as np
from timezonefinder import TimezoneFinder
import pytz

# import flights data ----------------------------------------------

flights = pd.read_csv('../data/raw_data/flights.csv')

flights_clean = flights.sort_values(by = ['time_hour'])
flights_clean['dep_delay_true'] = flights_clean['dep_delay'] > 15
flights_clean.dropna(inplace = True)

# import airports data --------------------------------------------
airports = pd.read_csv("../data/raw_data/airports.csv")

# add missing timezones to airports data
tf = TimezoneFinder()
tf_func = tf.timezone_at

airports['timezone'] = airports.apply(
    lambda row: tf_func(lng=row['lon'], lat=row['lat']), axis=1)


airports_clean = airports.drop(
    columns = ['tz', 'dst', 'tzone'])

airports_clean.rename(columns={'name':'airport'}, inplace=True)

# set timezone to datetime object
airports_clean['timezone'] = airports_clean.apply(
    lambda row: pytz.timezone(row['timezone']), axis=1)

# import weather data --------------------------------------------
weather = pd.read_csv('../data/raw_data/weather.csv')

# import additional weather data 
extra_weather = pd.read_csv('../data/raw_data/extra_weather.csv')
extra_weather.drop(columns = ['hdd', 'ccd'], inplace = True)

extra_weather.rename(columns = {'airport':'origin'}, inplace = True)

# change T (trace) to 0.01 in ppt, new_snow and snow_depth columns
extra_weather = extra_weather.replace({
    'ppt' : {'T':0.01},
    'new_snow' : {'T':0.01},
    'snow_depth' : {'T':0.01}})

# make joining id column for joining to weather data
extra_weather['join_id'] = extra_weather['date'] + '-' + extra_weather['origin']
extra_weather.drop(columns = ['date', 'origin'], inplace = True)

# format day and month in weather data for joining id column
weather['day_str'] = weather['day'].astype(str).str.zfill(2)
weather['month_str'] = weather['month'].astype(str).str.zfill(2)

weather['date'] = weather['year'].astype(str) +\
 '-' + weather['month_str'] + '-' + weather['day_str']

weather['join_id'] = weather['date'] + '-' + weather['origin']
weather.drop(columns = ['day_str', 'month_str'], inplace = True)

# note: weather is missing all data for dec 31st

weather_merge = pd.merge(
    left = weather, 
    right = extra_weather, 
    left_on = ['join_id'], 
    right_on = ['join_id'], 
    how = 'left')

# impute missing values in weather
# fill with median or mean depending on distribution of the original data
weather_merge.fillna({'visib': np.round(
    weather_merge.groupby('join_id').visib.transform('median'), 2)}, inplace = True)

weather_merge.fillna({'wind_dir': np.round(
    weather_merge.groupby('join_id').wind_dir.transform('median'), 2)}, inplace = True)

weather_merge.fillna({'wind_speed': np.round(
    weather_merge.groupby('join_id').wind_speed.transform('mean'), 2)}, inplace = True)

weather_merge.fillna({'wind_gust': np.round(
    weather_merge.groupby('join_id').wind_gust.transform('mean'), 2)}, inplace = True)

# remove columns not needed
weather_clean = weather_merge.copy()
weather_clean.drop(columns = [
    'temp', 
    'dewp', 
    'humid', 
    'precip', 
    'pressure', 
    'year', 
    'join_id'], 
    inplace = True)

# import planes data ---------------------------------------------------

planes = pd.read_csv('../data/raw_data/planes.csv')
planes_clean = planes.drop(
    columns = ['speed', 'seats', 'year', 'engines']
    )

# import airlines data -------------------------------------------------

airlines = pd.read_csv('../data/raw_data/airlines.csv')
airlines_clean = airlines.rename(columns={'name':'carrier_name'})


# joining datasets ------------------------------------------------------

# flights and weather

# time_hour in flights and weather does not make sense
# make a new column for joining based on month, day, hour and origin
flights_clean['join_id'] = flights_clean['month'].astype(str) +\
      '-' + flights_clean['day'].astype(str) +\
     '-' + flights_clean['hour'].astype(str) +\
     '-' + flights_clean['origin']

weather_clean['join_id'] = weather_clean['month'].astype(str) +\
     '-' + weather_clean['day'].astype(str) +\
     '-' + weather_clean['hour'].astype(str) +\
     '-' + weather_clean['origin']

# drop duplicated columns
weather_clean.drop(
    columns = ['month', 'day', 'hour', 'origin', 'time_hour'], inplace = True
    )

# make flights_airports_weather
flights_weather = pd.merge(left = flights_clean, right = weather_clean,\
     left_on = ['join_id'], right_on = ['join_id'], how = 'left')

# drop rows from the day with the missing weather (dec 31st)
flights_weather.dropna(inplace = True)
flights_weather.drop(
    columns = ['join_id', 'date', 'year'], inplace = True
)

# flights, weather and airports

# add ori_ and dest_ prefix to airports before joining
airports_clean_ori = airports_clean.add_prefix('ori_').copy()
airports_clean_dest = airports_clean.add_prefix('dest_').copy()

flights_airports_ori = pd.merge(
    left = flights_weather, 
    right = airports_clean_ori, 
    left_on = ['origin'], 
    right_on = ['ori_faa'], 
    how = 'left')


flights_airports_weather = pd.merge(
    left = flights_airports_ori, 
    right = airports_clean_dest, 
    left_on = ['dest'], 
    right_on = ['dest_faa'], 
    how = 'left')

# make flights_airports_weather_airlines
flights_airports_weather_airlines = pd.merge(left = flights_airports_weather, right = airlines_clean,\
     left_on = ['carrier'], right_on = ['carrier'], how = 'left')


# make flights_airports_weather_airlines_planes
flights_airports_weather_airlines_planes = pd.merge(left = flights_airports_weather_airlines, right = planes_clean,\
     left_on = ['tailnum'], right_on = ['tailnum'], how = 'left')

# replace NaNs in plane data
na_replace = {
       'type': 'Unknown',
       'manufacturer': 'Unknown', 
       'model': 'Unknown', 
       'engine': 'Unknown'}

flights_airports_weather_airlines_planes.fillna(value=na_replace, inplace=True)


# write clean data
# note NaNs present in destination airport geospatial info

flights_airports_weather_airlines_planes.to_csv(path_or_buf='../data/clean_data/flights_data.csv')

