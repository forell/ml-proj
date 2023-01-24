#!/usr/bin/env python3
import csv
import osmium
import sys
import argparse

"""
Relevant values for the 'railway' tag.
https://wiki.openstreetmap.org/wiki/Key:railway
"""
train_station_types = ['station', 'halt', 'service_station']


def get_all_names(o):
    names = []

    if (name := o.tags.get('name')) is not None:
        names.append(name)

    if (alt_names := o.tags.get('alt_name')) is not None:
        names.extend(alt_names.split(';'))

    return names


def update_stations(stations, node, subst, names):
    for name in map(subst, names):
        if name in stations:
            stations[name] = node.location


class StationHandler(osmium.SimpleHandler):
    def __init__(self, stations, subst):
        super(StationHandler, self).__init__()
        self.stations = stations
        self.subst = subst


    def node(self, n):
        if n.tags.get('railway') in train_station_types:
            update_stations(self.stations, n, self.subst, get_all_names(n))


    def way(self, w):
        if w.tags.get('railway') in train_station_types:
            # Just grab any old node for now: since it's marked as a station,
            # presumably it's not especially large and we won't be off by much,
            # and the particular entry is misusing the 'railway' tag anyway.
            node = w.nodes[0]
            update_stations(self.stations, node, self.subst, get_all_names(w))


if __name__ == '__main__':
    argpar = argparse.ArgumentParser()
    argpar.add_argument('osm_file')
    argpar.add_argument('stations_file')
    argpar.add_argument('-s', '--name-substitutions')
    argpar.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout)

    args = argpar.parse_args()

    with open(args.stations_file, 'r') as f:
        stations = { name.strip() : None for name in f }

    subst_dict = {}

    if args.name_substitutions is not None:
        with open(args.name_substitutions, 'r') as f:
            for l in f:
                [orig, replace] = l.strip().split(',')
                subst_dict[orig] = replace

    def subst(orig):
        return subst_dict.get(orig, orig)

    station_handler = StationHandler(stations, subst)
    station_handler.apply_file(args.osm_file, locations = True)

    writer = csv.DictWriter(args.output, ['station', 'lat', 'lon'])
    writer.writeheader()
    for st, loc in station_handler.stations.items():
        if loc is not None:
            lat, lon = loc.lat, loc.lon
        else:
            lat, lon = None, None

        writer.writerow({ 'station' : st, 'lat' : lat, 'lon' : lon })
