#!/usr/bin/env python3
import csv
import json
import geopy.distance as geo
import numpy as np
import pandas as pd

"""
The columns used as input for the prediction.

Available columns:
TMAX — max temperature              [°C]
TMIN — min temperature              [°C]
STD  — mean temperature             [°C]
TMNG — min ground-level temperature [°C]
SMDB — total precipitation          [mm]
opad — type of precipation          [0 — rain, 1 — snow]
PKSN — snow cover height            [cm]
RWSN — snow water equivalent        [mm/cm]
USL  — sunshine duration            [hours]
DESZ — rainfall duration            [hours]
SNEG — snowfall duration            [hours]
DISN — mixed rain and snow duration [hours]
GRAD — hail duration                [hours]
MGLA — fog duration                 [hours]
ZMGL — mist duration                [hours]
SADZ — rime ice duration            [hours]
GOLO — black ice duration           [hours]
ZMNI — drifting snow duration       [hours]
ZMWS — ground blizzard duration     [hours]
ZMET — haze duration                [hours]
FF10 — wind speed ≥ 10 m/s duration [hours]
FF15 — wind speed > 15 m/s duration [hours]
BRZA — thunderstorm duration        [hours]
ROSA — dew duration                 [hours]
SZRO — frost duration               [hours]
DZPS — snow cover                   [0/1]
DZBL — lightning                    [0/1]
grun — ground frozen                [0/1]
IZD
IZG
AKTN
"""
weather_labels = ['TMAX', 'TMIN', 'STD', 'TMNG', 'SMDB', 'opad', 'PKSN',
                  'RWSN', 'USL', 'DESZ', 'SNEG', 'DISN', 'GRAD', 'MGLA',
                  'ZMGL', 'SADZ', 'GOLO', 'ZMNI', 'ZMWS', 'ZMET', 'FF10',
                  'FF15', 'BRZA', 'ROSA', 'SZRO', 'DZPS', 'DZBL', 'grun',
                  'IZD', 'IZG', 'AKTN']


num_of_weather_attr = len(weather_labels)


def load_data(weather_path, delay_path):
    def weather_to_numpy(coords, data):
        data = [ list(data[coord].values()) for coord in coords ]
        return np.array(data).T

    weather = dict()
    coords = set()

    with open(weather_path, 'r') as weather_data:
        for l in weather_data:
            measurement = json.loads(l)
            date = measurement['date']
            lat = measurement['lat']
            lon = measurement['lon']
            measurement = { k : measurement[k] for k in weather_labels }
            weather.setdefault(date, {})[(lat, lon)] = measurement
            coords.add((lat, lon))

    coords = list(coords)
    weather = { k : weather_to_numpy(coords, v) for k, v in weather.items() }

    with open(delay_path, 'r') as delay_data:
        delays = list(csv.reader(delay_data))

    return weather, coords, delays

    
def calculate_coefficients(weather_coords, lat, lon):
    dists_list = [geo.distance(coord, (lat, lon)).km for coord in weather_coords]
    dists = np.array(dists_list)
    weights = np.exp(-dists)
    return weights, np.sum(weights)
    
    
def weather_at(weather, date, coeffs_info):
    coeffs, coeffs_sum = coeffs_info        
    day_weather = weather[date]
    return np.sum(coeffs * day_weather, axis=-1)/coeffs_sum


def combine_data(weather, weather_coords, delays):
    X_weather = []
    Y_delays = []
    
    # dict of dicts: (point -> (date -> weather)) 
    weather_middlepoints = dict()
    # point -> (table of coefficients e^(-d), sum of this table)
    coeffs = dict()
    
    for d in delays:
        lat, lon, date, delay = d
        if (lat, lon) not in weather_middlepoints:
            weather_middlepoints[(lat, lon)] = dict()
            coeffs[(lat, lon)] = calculate_coefficients(weather_coords, lat, lon)
        if date not in weather_middlepoints[(lat, lon)]:
            weather_middlepoints[(lat, lon)][date] = weather_at(weather, date, coeffs[(lat, lon)])
        X_weather.append(weather_middlepoints[(lat, lon)][date])
        Y_delays.append(delay)

    return np.array(X_weather), np.array(Y_delays)[np.newaxis]


def main():
    weather, weather_coords, delays = load_data('data/weather_readings.json', 'data/minidelays.csv')
    X, y = combine_data(weather, weather_coords, delays)


if __name__ == '__main__':
    main()
