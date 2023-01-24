#!/usr/bin/env python3

import os
import csv
import json
import re
import sys
from argparse import ArgumentParser
from io import TextIOWrapper
from shutil import copyfileobj
from urllib.request import urlopen
from zipfile import ZipFile


coord = {}


def load_coord():
    with open('data/weather_stations.csv') as fp:
        for code, name, lon, lat in csv.reader(fp):
            lat, lon = map(parse_coord, (lat, lon))
            coord[int(code)] = lat, lon


def parse_coord(dat):
    return sum(float(v) / 60**i for i, v in enumerate(dat.split()))


def onepath(path, download=False):
    fn = os.path.basename(path)
    m = re.match(r'^(\d{4})_([01]\d)_([sok])\.zip$', fn)
    if not m:
        print("unable to infer year and month from filename; "
              "use format 2022_07_s.zip", repr(fn))
        sys.exit(1)

    year = int(m.group(1))
    month = int(m.group(2))
    category = ('synop', 'opad', 'klimat')['sok'.index(m.group(3))]

    try:
        fp = open(path, 'rb')
    except FileNotFoundError:
        if not download:  raise
        fp = open(path, 'w+b')
        req = urlopen(
            'http://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/'
            f'dane_meteorologiczne/dobowe/{category}/'
            f'{year}/{year}_{month:02}_{category[0]}.zip'
        )
        copyfileobj(req, fp)

    with fp:
        z = ZipFile(fp)
        uncompressed = z.open(f'{category[0]}_d_{month:02}_{year}.csv')

        assert category == 'synop'
        onezip(uncompressed)


def onezip(uncompressed):
    reader = csv.reader(TextIOWrapper(uncompressed, 'cp1250'))

    labels = '''
    code name year month date
    TMAX TMAXs TMIN TMINs STD  STDs  TMNG TMNGs SMDB SMDBs opad
    PKSN PKSNs RWSN RWSNs USL  USLs  DESZ DESZs SNEG SNEGs DISN DISNs
    GRAD GRADs MGLA MGLAs ZMGL ZMGLs SADZ SADZs GOLO GOLOs
    ZMNI ZMNIs ZMWS ZMWSs ZMET ZMETs FF10 FF10s FF15 FF15s
    BRZA BRZAs ROSA ROSAs SZRO SZROs DZPS DZPSs DZBL DZBLs grun
    IZD  IZDs  IZG  IZGs  AKTN AKTNs
    '''.split()

    for row in reader:
        assert len(row) == len(labels)
        d = {}
        for label, value in zip(labels, row):
            if label[-1] == 's':  # 8 = not measured, 9 = measured to be absent
                # don't care XD
                continue

            if label == 'opad':
                value = 'WS'.index(value)
            elif label == 'grun':
                value = 'RZ'.index(value)
            elif label.isupper():
                value = float(value or 0)
            elif label == 'code':
                lat, lon = coord[int(value) % 1000]
                d['lat'] = lat
                d['lon'] = lon
                continue
            elif label == 'name':
                continue
            else:
                value = int(value)
            d[label] = value
        dt = f'''{d.pop('year')}-{d.pop('month'):02}-{d.pop('date'):02}'''
        d['date'] = dt
        print(json.dumps(d))


if __name__ == '__main__':
    par = ArgumentParser()
    par.add_argument('--download', action='store_true')
    par.add_argument('path', nargs='+')

    arg = par.parse_args()

    load_coord()
    for path in arg.path:
        onepath(path, arg.download)
