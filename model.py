#!/usr/bin/env python3
import json
import csv
import pandas as pd
import numpy as np

"""The columns used as input for the prediction."""
weather_labels = ['TMAX', 'TMIN', 'STD', 'TMNG', 'SMDB', 'opad', 'PKSN',
                  'RWSN', 'USL', 'DESZ', 'SNEG', 'DISN', 'GRAD', 'MGLA',
                  'ZMGL', 'SADZ', 'GOLO', 'ZMNI', 'ZMWS', 'ZMET', 'FF10',
                  'FF15', 'BRZA', 'ROSA', 'SZRO', 'DZPS', 'DZBL', 'grun',
                  'IZD', 'IZG', 'AKTN']

def load_data(weather_path, delay_path):
    weather = {}
    with open(weather_path, 'r') as weather_data:
        for l in weather_data:
            measurement = json.loads(l)
            date = measurement.pop('date')
            weather.setdefault(date, []).append(measurement)

    fields = ['lat', 'lon', 'date', 'delay']
    with open(delay_path, 'r') as delay_data:
        delays = [ dict(zip(fields, row)) for row in csv.reader(delay_data) ]

    return weather, delays


def weather_at(weather, date, lat, lon):
    # TODO:
    return { k : v for k, v in weather[date][0].items() if k not in ['lat', 'lon'] }


def combine_data(weather, delays):
    data = []

    for d in delays:
        row = weather_at(weather, d['date'], lat=d['lat'], lon=d['lon'])
        data.append(row | { 'delay' : d['delay'] })
    
    return pd.DataFrame(data)


def main():
    weather, delays = load_data('data/weather_readings.json', 'data/minidelays.csv')
    dt = combine_data(weather, delays)
    X = dt[weather_labels]
    y = dt['delay']


if __name__ == '__main__':
    main()
