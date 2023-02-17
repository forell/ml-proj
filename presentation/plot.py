#!/usr/bin/env python3
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

mapcolor = '#242424'
wcolor   = '#d5cb57'
rcolor   = '#da4141'


# The same as in `czystapogoda.py`; maybe the data file should be formatted as
# expected in the first place.
def parse_coord(dat):
    return sum(float(v) / 60**i for i, v in enumerate(dat.split()))


def df_to_gdf(df):
    return gpd.GeoDataFrame([],
                            geometry=gpd.points_from_xy(df['lon'], df['lat']),
                            crs='epsg:4326')


def create_axis(area):
    ax = area.plot(color=mapcolor, edgecolor=mapcolor)
    ax.margins(0)
    return ax


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(f'usage: {sys.argv[0]} path')
        sys.exit(1)

    area = gpd.read_file(sys.argv[1])

    weather = pd.read_csv('../data/weather_stations.csv', names=['lon', 'lat'],
                          usecols=[2, 3])

    weather = weather.applymap(parse_coord)
    weather = df_to_gdf(weather).to_crs(area.crs)

    railway = pd.read_csv('../data/railway_stations.csv', usecols=[1, 2])

    railway = df_to_gdf(railway).to_crs(area.crs)

    weather.plot(ax=create_axis(area), color=wcolor, markersize=15).set_axis_off()
    plt.savefig('images/weather.pdf', transparent=True, bbox_inches='tight',
                pad_inches=0)

    ax = create_axis(area)
    railway.plot(ax=ax, color=rcolor, markersize=5).set_axis_off()
    plt.savefig('images/railway.pdf', transparent=True, bbox_inches='tight',
                pad_inches=0)

    weather.plot(ax=ax, marker='o', color=wcolor, markersize=15).set_axis_off()
    plt.savefig('images/weather_railway.pdf', transparent=True,
                bbox_inches='tight', pad_inches=0)
