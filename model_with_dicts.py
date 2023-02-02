#!/usr/bin/env python3
import csv
import json
import geopy.distance as geo
import numpy as np
import pandas as pd

"""The columns used as input for the prediction."""
weather_labels = ['TMAX', 'TMIN', 'STD', 'TMNG', 'SMDB', 'opad', 'PKSN',
                  'RWSN', 'USL', 'DESZ', 'SNEG', 'DISN', 'GRAD', 'MGLA',
                  'ZMGL', 'SADZ', 'GOLO', 'ZMNI', 'ZMWS', 'ZMET', 'FF10',
                  'FF15', 'BRZA', 'ROSA', 'SZRO', 'DZPS', 'DZBL', 'grun',
                  'IZD', 'IZG', 'AKTN']

# num_of_weather_attr = len(weather_labels) # ??
num_of_weather_attr = 2

def load_data(weather_path, delay_path):
    """
    TODO: real weather!!!
   
    """        
    # dumb weather for test (5 weather stations; 3 dates (only these in dumb_delays.csv), 2 parameters of wether)
    station_coors = [(52.8758646, 18.6963912), (49.8557919, 19.3533583), (49.858467, 19.323956), (49.3406059, 20.8209928), (53.1291537, 17.4865518)]
    weather = dict()
    weather["2019-08-31"] = np.arange(10).reshape(2, 5)
    weather["2019-09-01"] = -np.arange(10).reshape(2, 5)
    weather["2019-09-02"] = np.arange(10).reshape(2, 5)**2

    with open(delay_path, 'r') as delay_data:
        delays = [row for row in csv.reader(delay_data)]

    return weather, station_coors, delays

    
def calculate_coefficients(weather_stations_coors, lat, lon):
    dists_list = [geo.distance(station_coor, (lat, lon)).km for station_coor in weather_stations_coors]
    dists = np.array(dists_list)
    weights = np.e ** -dists
    return weights, np.sum(weights)
    
    
def weather_at(weather, date, coeffs_info):
    coeffs, coeffs_sum = coeffs_info        
    day_weather = weather[date]
    return np.sum(coeffs * day_weather, axis=-1)/coeffs_sum


def combine_data(weather, weather_stations_coords, delays):
    X_weather = np.empty((0, num_of_weather_attr))
    Y_delays = np.empty((0, 1))
    
    # dict of dicts: (point -> (date -> weather)) 
    weather_middlepoints = dict()
    # point -> (table of coefficients e^(-d), sum of this table)
    coeffs = dict()
    
    for d in delays:
        lat, lon, date, delay = d
        if (lat, lon) not in weather_middlepoints:
            weather_middlepoints[(lat, lon)] = dict()
            coeffs[(lat, lon)] = calculate_coefficients(weather_stations_coords, lat, lon)
        if date not in weather_middlepoints[(lat, lon)]:
            weather_middlepoints[(lat, lon)][date] = weather_at(weather, date, coeffs[(lat, lon)])
        row = weather_middlepoints[(lat, lon)][date].reshape(1, -1)
        X_weather = np.concatenate((X_weather, row))
        Y_delays = np.concatenate((Y_delays, np.array([[delay]])))

    return X_weather, Y_delays


def main():
    weather, station_coords, delays = load_data('tu cokolwiek na razie', 'dumb_delays.csv')
    X_weather, Y_delays = combine_data(weather, station_coords, delays)


if __name__ == '__main__':
    main()
    
    
